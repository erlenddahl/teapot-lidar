import numpy as np
import json
import math
import time
import os
from tqdm import tqdm
import open3d as o3d
import laspy
from datetime import datetime
from utils.taskTimer import TaskTimer
from algorithmHelper import AlgorithmHelper
from pcap.pcapReaderHelper import PcapReaderHelper
from utils.open3dVisualizer import Open3DVisualizer
from utils.plotter import Plotter
from sbet.sbetParser import SbetRow
import argparse

class NavigatorBase:

    def __init__(self, args, min_frame_limit = 1):
        self.timer = TaskTimer()

        self.args = args

        self.reader = PcapReaderHelper.from_lists(args.pcap, args.json, args.skip_every_frame, args=args)
        self.voxel_size = args.voxel_size
        self.matcher = AlgorithmHelper.get_algorithm(args.algorithm)
        self.remove_vehicle = True
        self.frame_limit = args.frames
        self.preview_always = args.preview == "always"
        self.preview_at_end = args.preview == "always" or args.preview =="end"
        self.no_preview = self.preview_always == False and self.preview_at_end == False
        self.save_path = args.save_to
        self.downsample_timer = args.downsample_after
        self.downsample_cloud_after_frames = args.downsample_after
        self.merged_frame_is_dirty = True
        self.save_screenshots_to = args.save_screenshots_to
        self.save_frame_pairs_to = args.save_frame_pairs_to
        self.save_frame_pair_threshold = args.save_frame_pair_threshold
        self.previous_transformation = None
        self.skip_start = args.skip_start
        self.build_cloud_timer = args.build_cloud_after
        self.build_cloud_after = args.build_cloud_after
        self.build_cloud = args.build_cloud_after > 0
        self.raise_on_error = args.raise_on_error
        self.raise_on_movement = args.raise_on_movement
        self.has_waited = False
        self.wait_after_initial_frame = args.wait_after_initial_frame
        self.full_point_cloud_offset = None

        self.skip_until_circle_center = None
        if self.args.skip_until_radius > 0 and self.args.skip_until_x is not None and self.args.skip_until_x is not None:
            self.skip_until_circle_center = SbetRow(None, x=self.args.skip_until_x, y=self.args.skip_until_y)

        if args.skip_start > 0 and self.skip_until_circle_center is not None:
            raise Exception("Cannot use both --skip-start and --skip-until-[x/y/radius] at the same time!")
        
        self.tqdm_config = { "ascii": True }
        self.print_summary_at_end = False

        self.current_coordinate = None
        
        self.position_cylinder_radius = 1
        self.position_cylinder_height = 20
        
        self.time("setup")

        if self.frame_limit <= min_frame_limit:
            self.frame_limit = self.reader.count_frames(True)
            self.time("frame counting")

    def skip_initial_frames(self):
        """ Skips frames at the beginning of the given pcap file(s). The number of skipped frames is given by the
        --skip-start argument.
        """

        if self.skip_start <= 0:
            return

        self.skip_to_frame(self.skip_start, "Skipping frames")

    def skip_to_frame(self, frame_index, desc):
        self.frame_limit -= frame_index
        for _ in tqdm(range(0, frame_index), desc=desc, **self.tqdm_config):
            self.reader.next_frame(False, self.timer)

    def skip_until_circle(self):
        """ The "skip until" circle is used to skip frames until the actual position has entered a circle given by the 
        --skip-until-x, --skip-until-y, and --skip-until-radius arguments. It is intended as a simple way of creating
        sub routes that start at the exact same point, even though pcap files start and stop at different points for 
        different trips.
        """

        if self.skip_until_circle_center is None:
            return

        skip_until = -1
        for (ix, position) in enumerate(self.sbet_coordinates):
            distance = self.skip_until_circle_center.distance2d(position)
            if distance <= self.args.skip_until_radius:
                skip_until = ix
                break

        if skip_until < 0:
            raise Exception("The actual position never entered the circle given by --skip-until-[x/y/radius].")

        self.skip_to_frame(skip_until, "Skipping until entering circle")

    def initialize_navigation(self, initial_movement=[], rotate_sbet=False):
        self.timer.reset()
        self.skip_initial_frames()

        # Initialize the list of movements as well as the merged frame, and the first 
        # source frame.
        self.movements = []
        self.registration_configs = []
        self.actual_coordinates = []
        self.estimated_coordinates = []
        self.sbet_coordinates = []
        self.actual_movement_path = None

        self.movement_path = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector(initial_movement), lines=o3d.utility.Vector2iVector([])
        )

        if self.args.sbet is not None:

            # Read the coordinates from all frames in the PCAP file(s).
            # We set the rotate-argument to False, since we're working with
            # the same coordinate system here -- both the georeferenced point cloud
            # and the actual coordinates of the frames are in UTM, and there is
            # therefore no need to rotate them like it is in the visual odometry
            # based navigator.
            self.sbet_coordinates = self.reader.get_coordinates(rotate=rotate_sbet, show_progress=True)

            if self.full_point_cloud_offset is not None:
                # Translate all coordinates towards origo with the same offset as
                # the point cloud.
                for c in self.sbet_coordinates:
                    c.translate(-self.full_point_cloud_offset)

                # Also translate the "skip until" circle 
                if self.skip_until_circle_center is not None:
                    self.skip_until_circle_center.translate(-self.full_point_cloud_offset)
        
        self.skip_until_circle()

    def finalize_navigation(self, navigation_exception):

        # When everything is finished, print a summary, and save the point cloud and debug data.
        if self.preview_at_end:
            self.plot.show_plot()
            self.plot.update()

        results = self.check_results_saving(True)
        self.finish_plot_and_visualization()

        if navigation_exception is not None:
            raise navigation_exception

        return results

    def create_cylinder(self, size_ratio=1, color=[0,0,1]):
        cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=self.position_cylinder_radius * size_ratio, height=self.position_cylinder_height * (2 - size_ratio), resolution=20, split=4)
        cylinder.paint_uniform_color(color)
        return cylinder

    def create_line(self, points, color=[0,0,1]):
        line = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector(points), 
            lines = o3d.utility.Vector2iVector([[i, i+1] for i in range(len(points) - 1)])
        )
        line.paint_uniform_color(color)
        return line

    @staticmethod
    def print_cloud_info(title, cloud, prefix = ""):
        mf = np.asarray(cloud.points)

        print(prefix + title + ":")

        if len(mf) < 1:
            print("    > Empty array")
            return

        mins = np.amin(mf, axis=0)
        maxs = np.amax(mf, axis=0)

        print(prefix + "    > X: {:.2f} - {:.2f}".format(mins[0], maxs[0]))
        print(prefix + "    > Y: {:.2f} - {:.2f}".format(mins[1], maxs[1]))
        print(prefix + "    > Z: {:.2f} - {:.2f}".format(mins[2], maxs[2]))

    def ensure_merged_frame_is_downsampled(self):

        if self.voxel_size <= 0:
            return

        if not self.merged_frame_is_dirty:
            return

        self.merged_frame = self.merged_frame.voxel_down_sample(voxel_size=self.voxel_size)
        self.merged_frame_is_dirty = False
        self.time("cloud downsampling")

    @staticmethod
    def ensure_dir(file_path):
        directory = os.path.dirname(file_path)
        if len(directory) < 1: 
            return
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get_results(self):
        data = self.plot.get_json(self.timer)

        data["movement"] = np.asarray(self.movement_path.points).tolist()
        data["algorithm"] = self.matcher.name

        return data

    @staticmethod
    def save_data(path, data):

        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def save_cloud_as_las(path, cloud):

        xyz = np.asarray(cloud.points)

        las = laspy.create(point_format=3, file_version="1.4")
        
        xmin = np.floor(np.min(xyz[:,0]))
        ymin = np.floor(np.min(xyz[:,1]))
        zmin = np.floor(np.min(xyz[:,2]))

        las.header.offset = [xmin, ymin, zmin]
        las.header.scale = [0.001, 0.001, 0.001]
        las.x = xyz[:,0]
        las.y = xyz[:,1]
        las.z = xyz[:,2]

        las.write(path)

    def check_save_frame_pair(self, source, target, reg):
        """ Saves the frame pair if enabled and fitness is below threshold. """

        if self.save_frame_pairs_to is None: 
            return

        if reg.fitness >= self.save_frame_pair_threshold:
            return

        filenameBase = os.path.join(self.save_frame_pairs_to, str(reg.fitness) + "_" + os.path.basename(self.reader.pcap_path).replace(".pcap", "") + "_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f%z'))
        self.ensure_dir(filenameBase)
        o3d.io.write_point_cloud(filenameBase + "_a.pcd", source, compressed=True)
        o3d.io.write_point_cloud(filenameBase + "_b.pcd", target, compressed=True)
    
    def time(self, key):
        return self.timer.time(key)

    def check_save_screenshot(self, index, ensure_dir = False):
        if self.save_screenshots_to is None:
            return
        
        screenshot_path = os.path.join(self.save_screenshots_to, str(index) + ".png")

        if ensure_dir:
            self.ensure_dir(screenshot_path)

        self.vis.capture_screen_image(screenshot_path)

        self.time("saved screenshot")

    def initialize_plot_and_visualization(self):
        # Initialize the visualizer
        self.vis = Open3DVisualizer(add_axes=False)

        if self.preview_always:

            # Initiate non-blocking visualizer window
            self.vis.refresh_non_blocking()

            # Show the first frame and reset the view
            if self.merged_frame is not None:
                self.vis.show_frame(self.merged_frame)
            
            self.vis.set_follow_vehicle_view()

            if self.actual_movement_path is not None:
                self.vis.add_geometry(self.actual_movement_path, True)

            self.check_save_screenshot(0, True)

        self.plot = Plotter(self.preview_always)

    def finish_plot_and_visualization(self):
        
        if self.print_summary_at_end:
            self.plot.print_summary(self.timer)

        # Then continue showing the visualization in a blocking way until the user stops it.
        if self.preview_at_end:
            if self.merged_frame is not None:
                self.vis.show_frame(self.merged_frame)

            if self.movement_path is not None:
                self.vis.remove_geometry(self.movement_path)
                self.vis.add_geometry(self.movement_path)

            if self.actual_movement_path is not None:
                self.vis.remove_geometry(self.actual_movement_path)
                self.vis.add_geometry(self.actual_movement_path)

            self.vis.reset_view()

            self.vis.run()

        self.plot.destroy()

    def calculate_distance_between_points(self, x1, y1, x2, y2, heading):
        """ Calculates the distances between the two given points along and
        across the given heading.
        Returns (along, across).
        Along: positive means p1 is ahead of p2.
        Across: positive means p1 is to the left of the movement vector of p2.
        """

        # Calculate the straight distance between the points
        dx = x1-x2;
        dy = y1-y2;
        c = math.sqrt(dx*dx + dy*dy);
        
        # Calculate the angle between the X axis and the straight line between the points
        xAngle = math.atan(dy/dx);
        
        # The angle in the triangle formed by C and the along/across distances is PI/2 minus the heading and the xAngle
        alpha = math.pi/2 + heading + xAngle;
        
        # Now we can calculate the two remaining sides:
        return (c * math.cos(alpha), c * math.sin(alpha))

    def update_plot(self, reg, registration_time, movement, actual_coordinate):
        self.plot.timeUsages.append(registration_time)
        self.plot.rmses.append(reg.inlier_rmse)
        self.plot.fitnesses.append(reg.fitness)
        self.plot.distances.append(np.sqrt(np.dot(movement, movement)))

        # Append the newest movement
        self.movements.append(movement)

        if self.current_coordinate is not None:

            # Add the current coordinate to the list of estimations
            self.estimated_coordinates.append(self.current_coordinate.clone())
            self.actual_coordinates.append(actual_coordinate.clone())

            # Calculate differences between the estimate and the actual coordinate
            dx = abs(self.current_coordinate.x - actual_coordinate.x)
            dy = abs(self.current_coordinate.y - actual_coordinate.y)
            dz = self.current_coordinate.alt - actual_coordinate.alt

            # Calculate distances along and across of the movement vector (heading)
            dist = self.calculate_distance_between_points(self.current_coordinate.x, self.current_coordinate.y, actual_coordinate.x, actual_coordinate.y, actual_coordinate.heading)

            # Save all values in the plot collection
            self.plot.position_error_along_heading.append(dist[0])
            self.plot.position_error_across_heading.append(dist[1])
            self.plot.position_error_x.append(dx)
            self.plot.position_error_y.append(dy)
            self.plot.position_error_z.append(dz)
            self.plot.position_error_2d.append(np.sqrt(dx*dx+dy*dy))
            self.plot.position_error_3d.append(np.sqrt(dx*dx+dy*dy+dz*dz))
            self.plot.position_age.append(actual_coordinate.age)

        self.plot.step(self.preview_always)
        self.time("plot step")

        if self.raise_on_error > 0 and self.plot.position_error_3d[-1] > self.raise_on_error:
            raise Exception("The navigation error is larger than the given limit (--raise-on-error).")

        if self.raise_on_movement > 0 and self.plot.distances[-1] > self.raise_on_movement:
            raise Exception("The movement between the last two frames was larger than the given limit (--raise-on-movement).")           

    def check_results_saving(self, save_cloud = False):

        results = self.get_results()
        
        results["estimated_coordinates"] = [x.json() for x in self.estimated_coordinates]
        results["actual_coordinates"] = [x.json(True) for x in self.actual_coordinates]
        results["sbet_coordinates"] = [x.json(True) for x in self.sbet_coordinates]
        results["registration_configs"] = self.registration_configs

        results["args"] = vars(self.args)
        
        if self.save_path is not None:

            self.ensure_dir(os.path.join(self.save_path, "plot.png"))
            self.plot.save_plot(os.path.join(self.save_path, "plot.png"))

            if save_cloud and self.build_cloud:
                self.save_cloud_as_las(os.path.join(self.save_path, "cloud.laz"), self.merged_frame)
                o3d.io.write_point_cloud(os.path.join(self.save_path, "cloud.pcd"), self.merged_frame, compressed=True)

            self.time("results saving")
            
            self.save_data(os.path.join(self.save_path, "data.json"), results)

        return results

    def modify_cloud(self, cloud, translate=None, translate_relative=True, voxel_size=None, color=None):
        """ Modifies an Open3D PointCloud object (o3d.geometry.PointCloud) with the given transformations.
        """

        if voxel_size is not None:
            cloud = cloud.voxel_down_sample(voxel_size=voxel_size)

        if translate is not None:
            cloud.translate(np.array(translate), relative=translate_relative)

        if color is not None:
            cloud.paint_uniform_color(color)

        return cloud

    def check_wait(self):
        if self.has_waited or self.wait_after_initial_frame <= 0:
            return

        end_at = time.time() + self.wait_after_initial_frame
        with tqdm(desc="Waiting for vis. adjustment", total=self.wait_after_initial_frame, **self.tqdm_config) as pbar:
            while time.time() < end_at:
                self.vis.refresh_non_blocking()
                pbar.n = int(self.wait_after_initial_frame - end_at + time.time())
                pbar.refresh()

        self.has_waited = True

    def add_to_merged_frame(self, frame, handle_visualization=False):

        if not self.build_cloud:
            return

        if self.merged_frame is None:
            self.merged_frame = frame
            if handle_visualization:
                self.vis.add_geometry(self.merged_frame)
            
            return

        # Add the frame to the generated point cloud (unless we should skip some frames)
        self.build_cloud_timer -= 1
        if self.build_cloud_timer <= 0:

            # Combine the points from the merged visualization with the points from the next frame
            self.merged_frame += frame
            self.merged_frame_is_dirty = True
            self.build_cloud_timer = self.build_cloud_after

            self.time("cloud merging")

            # Downsample the merged visualization to make it faster to work with.
            # Otherwise it would grow extremely large, as it would contain all points
            # from all processed point clouds.
            # Don't do this on every frame, as it takes a lot of time.
            self.downsample_timer -= 1
            if self.downsample_timer <= 0:
                self.ensure_merged_frame_is_downsampled()
                self.downsample_timer = self.downsample_cloud_after_frames

            if handle_visualization:
                self.vis.update_geometry(self.merged_frame)

    @staticmethod
    def create_parser():
        parser = argparse.ArgumentParser()
        PcapReaderHelper.add_path_arguments(parser)
        return parser

    @staticmethod
    def add_standard_and_parse_args(parser):
        parser.add_argument('--algorithm', type=str, default="NICP", required=False, help="Use this registration algorithm (see names in algorithmHelper.py).")
        parser.add_argument('--frames', type=int, default=-1, required=False, help="If given a number larger than 1, only this many frames will be read from the PCAP file.")
        parser.add_argument('--build-cloud-after', type=int, default=1, required=False, help="How often registered frames should be added to the generated point cloud. 0 or lower deactivates the generated point cloud. 1 or higher generates a point cloud with details (and time usage) decreasing with higher numbers.")
        parser.add_argument('--skip-every-frame', type=int, default=0, required=False, help="If given a positive number larger than 0, this many frames will be skipped between every frame read from the PCAP file.")
        parser.add_argument('--skip-until-radius', type=int, default=20, required=False, help="If given together with --skip-until-x and --skip-until-y, the analysis will skip frames until the actual position enters the circle given by these three parameters.")
        parser.add_argument('--skip-until-x', type=float, default=None, required=False, help="If given together with --skip-until-x and --skip-until-radius, the analysis will skip frames until the actual position enters the circle given by these three parameters.")
        parser.add_argument('--skip-until-y', type=float, default=None, required=False, help="If given together with --skip-until-y and --skip-until-radius, the analysis will skip frames until the actual position enters the circle given by these three parameters.")
        parser.add_argument('--skip-start', type=int, default=0, required=False, help="If given a positive number larger than 0, this many frames will be skipped before starting processing frames.")
        parser.add_argument('--voxel-size', type=float, default=0.1, required=False, help="The voxel size used for cloud downsampling. If less than or equal to zero, downsampling will be disabled.")
        parser.add_argument('--downsample-after', type=int, default=10, required=False, help="The cloud will be downsampled (which is an expensive operation for large clouds, so don't do it too often) after this many registered frames have been added. If this number is higher than the number of frames being read, it will be downsampled once at the end of the process (unless downsampling is disabled, see --voxel-size).")
        parser.add_argument('--preview', type=str, default="always", choices=['always', 'end', 'never'], help="Show constantly updated point cloud and data plot previews while processing ('always'), show them only at the end ('end'), or don't show them at all ('never').")
        parser.add_argument('--save-to', type=str, default=None, required=False, help="If given, final results will be stored in this folder.")
        parser.add_argument('--save-screenshots-to', type=str, default=None, required=False, help="If given, point cloud screenshots will be saved in this directory with their indices as filenames (0.png, 1.png, 2.png, etc). Only works if --preview is set to 'always'.")
        parser.add_argument('--save-frame-pairs-to', type=str, default=None, required=False, help="If given, frame pairs with a registered fitness below --save-frame-pair-threshold will be saved to the given directory for manual inspection.")
        parser.add_argument('--save-frame-pair-threshold', type=float, default=0.97, required=False, help="If --save-frame-pairs-to is given, frame pairs with a registered fitness value below this value will be saved.")
        parser.add_argument('--skip-last-frame-in-pcap-file', type=bool, default=True, required=False, help="The last frame in each PCAP file is often corrupted. This flag makes the pcap reader skip the last frame in each file.")
        parser.add_argument('--raise-on-error', type=float, default=200, required=False, help="The frame processing will raise an exception if the distance between the actual and the estimated position is larger than this number. Set to 0 or lower to deactivate.")
        parser.add_argument('--raise-on-movement', type=float, default=100, required=False, help="The frame processing will raise an exception if the distance between two last estimated positions is larger than this number. Set to 0 or lower to deactivate.")
        parser.add_argument('--wait-after-initial-frame', type=int, default=0, required=False, help="If given, the analysis will wait for this many seconds after the first frame to allow the visualization to be manually adjusted (zooming, panning, etc).")

        args = parser.parse_args()

        if args.save_screenshots_to is not None and args.preview != "always":
            raise ValueError("Cannot save cloud screenshots without --preview being set to 'always'.")

        return args