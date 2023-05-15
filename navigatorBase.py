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

        self.visualization_window_name = self.args.visualization_window_name if self.args.visualization_window_name is not None else os.path.basename(os.path.normpath(args.pcap[0]))

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
        self.merged_frame = None
        self.merged_frame_is_dirty = True
        self.save_screenshots_to = args.save_screenshots_to
        self.save_frame_pairs_to = args.save_frame_pairs_to
        self.save_frame_pair_threshold = args.save_frame_pair_threshold
        self.previous_transformation = None
        self.skip_start = args.skip_start
        self.build_cloud_timer = args.build_cloud_after
        self.build_cloud_after = args.build_cloud_after
        self.build_cloud = args.build_cloud_after > 0
        self.has_waited = False
        self.wait_after_first_frame = args.wait_after_first_frame
        self.full_point_cloud_offset = None
        self.previous_matrix = None
        self.frame_index_offset = 0

        self.skip_until_circle_center = None
        self.skip_until_circle_center_cylinder = None
        if self.args.skip_until_radius > 0 and self.args.skip_until_x is not None and self.args.skip_until_y is not None:
            self.skip_until_circle_center = SbetRow(None, x=self.args.skip_until_x, y=self.args.skip_until_y)
            self.skip_until_circle_center.radius = self.args.skip_until_radius

        self.run_until_ix = -1
        self.run_until_circle_center = None
        self.run_until_circle_center_cylinder = None
        if self.args.run_until_radius > 0 and self.args.run_until_x is not None and self.args.run_until_y is not None:
            self.run_until_circle_center = SbetRow(None, x=self.args.run_until_x, y=self.args.run_until_y)
            self.run_until_circle_center.radius = self.args.run_until_radius

        if args.skip_start > 0 and self.skip_until_circle_center is not None:
            raise Exception("Cannot use both --skip-start and --skip-until-[x/y/radius] at the same time!")
        
        self.tqdm_config = { "ascii": True }
        self.print_summary_at_end = False

        self.current_estimated_coordinate = None
        
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

        skip_until, _ = self.find_first_frame_entering_circle(self.skip_until_circle_center)

        if skip_until < 0:
            raise Exception("The actual position never entered the circle given by --skip-until-[x/y/radius] (" + str(self.skip_until_circle_center.x) + ", " + str(self.skip_until_circle_center.y) + ", " + str(self.skip_until_circle_center.radius) + ").")

        self.skip_to_frame(skip_until, "Skipping until entering circle")

    def find_first_frame_entering_circle(self, circle):
        for (ix, position) in enumerate(self.sbet_coordinates):
            distance = circle.distance2d(position)
            if distance <= circle.radius:
                return (ix, position)

        return (-1, None)

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

        # Read the coordinates from all frames in the PCAP file(s).
        # We set the rotate-argument to False, since we're working with
        # the same coordinate system here -- both the georeferenced point cloud
        # and the actual coordinates of the frames are in UTM, and there is
        # therefore no need to rotate them like it is in the visual odometry
        # based navigator.
        self.sbet_coordinates = self.reader.get_coordinates(rotate=rotate_sbet, show_progress=True)

        # If there is no point cloud offset here (incremental navigation), create an
        # offset based on the SBET coordinates instead
        if self.full_point_cloud_offset is None:
            points = [[c.x, c.y, c.alt] for c in self.sbet_coordinates]
            mins = np.amin(points, axis=0)
            maxes = np.amax(points, axis=0)
            self.full_point_cloud_offset = mins + (maxes - mins) / 2
            tqdm.write("Using offset " + str(self.full_point_cloud_offset) + " (calculated from SBET)")
        else:
            tqdm.write("Using offset " + str(self.full_point_cloud_offset) + " (from point cloud metadata)")

        # Translate all coordinates towards origo with the same offset as
        # the point cloud.
        for c in self.sbet_coordinates:
            c.translate(-self.full_point_cloud_offset)

        if self.skip_until_circle_center is not None:
            
            # Translate the "skip until" circle 
            self.skip_until_circle_center.translate(-self.full_point_cloud_offset)

            # Then skip frames until the skip circle
            self.skip_until_circle()
        
        self.actual_movement_path = self.create_line([[p.x, p.y, p.alt] for p in self.sbet_coordinates], color=[0, 0, 1])

        self.actual_position_cylinder = self.create_cylinder(size_ratio=1, color=[0,0,1])
        self.estimated_position_cylinder = self.create_cylinder(size_ratio=1, color=[1,0,0])
        self.start_position_cylinder = self.create_cylinder(size_ratio=1, color=[1,1,1])

        self.initial_coordinate = self.get_current_actual_coordinate().clone()
        self.current_estimated_coordinate = self.initial_coordinate.clone()

        sbet_data = self.reader.get_sbet_data()
        tqdm.write(f"Coordinates transformed from CRS {sbet_data['crs_from']} to {sbet_data['crs_to']} with GPS epoch {sbet_data['gps_epoch']}")
        tqdm.write(f"Initial coordinate (actual and estimate): " + self.to_actual(self.current_estimated_coordinate).short_str())

        self.actual_position_cylinder.translate(self.initial_coordinate.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)
        self.estimated_position_cylinder.translate(self.initial_coordinate.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)
        self.start_position_cylinder.translate(self.initial_coordinate.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)

        if self.skip_until_circle_center is not None:
            
            # And set the altitude on the skip-circle to the same as the first coordinate to be processed,
            # to allow it to be visualized together with the movement paths.
            self.skip_until_circle_center.alt = self.initial_coordinate.alt - 5;

            # Create a flat cylinder to indicate the skip-circle in the visualization.
            self.skip_until_circle_center_cylinder = self.create_cylinder_exact(self.args.skip_until_radius / self.position_cylinder_radius, 0.5, [0.8,0.8,0.8])
            self.skip_until_circle_center_cylinder.translate(self.skip_until_circle_center.np(), relative=False)

        if self.run_until_circle_center is not None:

            # Translate the "run until" circle 
            self.run_until_circle_center.translate(-self.full_point_cloud_offset)

            # Calculate the ending frame
            self.run_until_ix, coordinate = self.find_first_frame_entering_circle(self.run_until_circle_center)
            if self.run_until_ix < 0:
                raise Exception("The actual position never entered the circle given by --run-until-[x/y/radius] (" + str(self.run_until_circle_center.x) + ", " + str(self.run_until_circle_center.y) + ", " + str(self.run_until_circle_center.radius) + ").")
                        
            # And set the altitude on the skip-circle to the same as the first coordinate to enter the circle,
            # to allow it to be visualized together with the movement paths.
            self.run_until_circle_center.alt = (coordinate.alt if coordinate is not None else self.initial_coordinate.alt) - 5;

            # Create a flat cylinder to indicate the skip-circle in the visualization.
            self.run_until_circle_center_cylinder = self.create_cylinder_exact(self.args.run_until_radius / self.position_cylinder_radius, 0.5, [0.8,0.8,0.8])
            self.run_until_circle_center_cylinder.translate(self.run_until_circle_center.np(), relative=False)

    def to_actual(self, coordinate):
        """ Translates the given local coordinate back to the global coordinate system using the point cloud offset.
        """

        return coordinate.clone().translate(self.full_point_cloud_offset)

    def finalize_navigation(self, navigation_exception):

        # When everything is finished, print a summary, and save the point cloud and debug data.
        if self.preview_at_end:
            self.plot.show_plot()
            self.plot.update()

        results = self.check_results_saving(True, exception=navigation_exception, finished=True)
        self.finish_plot_and_visualization()

        if navigation_exception is not None:
            raise navigation_exception

        return results

    def create_cylinder(self, size_ratio=1, color=[0,0,1]):
        return self.create_cylinder_exact(self.position_cylinder_radius * size_ratio, self.position_cylinder_height * (2 - size_ratio), color)

    def create_cylinder_exact(self, radius, height, color=[0,0,1]):
        cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=radius, height=height, resolution=20, split=4)
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

        tqdm.write(prefix + title + ":")

        if len(mf) < 1:
            tqdm.write("    > Empty array")
            return

        mins = np.amin(mf, axis=0)
        maxs = np.amax(mf, axis=0)

        tqdm.write(prefix + "    > X: {:.2f} - {:.2f}".format(mins[0], maxs[0]))
        tqdm.write(prefix + "    > Y: {:.2f} - {:.2f}".format(mins[1], maxs[1]))
        tqdm.write(prefix + "    > Z: {:.2f} - {:.2f}".format(mins[2], maxs[2]))

    def get_current_actual_coordinate(self):

        # Retrieve the index of the currently processed frame
        ix = self.reader.get_current_frame_index() + self.frame_index_offset

        # The frame index from the readers is the index of the last
        # read frame. If we haven't started reading yet, it will 
        # be -1. In that case, use the first frame (instead of the last)
        if ix < 0:
            ix = 0

        # Retrieve the SBET data for this frame, which has
        # already been transformed to fit the point cloud.
        pos = self.sbet_coordinates[ix]

        # Set the frame_ix as an additional parameter
        pos.frame_ix = ix

        return pos

    def rotate_frame(self, frame, coordinate=None):

        if coordinate is None:
            coordinate = self.current_estimated_coordinate

        # Rotate the frame using the current heading
        heading = coordinate.heading
        R = frame.get_rotation_matrix_from_xyz((coordinate.roll, coordinate.pitch, self.get_corrected_heading(heading)))
        frame.rotate(R, center=[0,0,0])
        self.time("frame rotation")

    def get_corrected_heading(self, heading):
        heading = heading - np.pi/2
        if heading < 0:
            heading_corrected = np.absolute(heading)
        elif heading > 0:
            heading_corrected = np.pi*2-heading
        return heading_corrected

    def calculate_heading(self, prev, curr):
        """ Calculates a headinv between the previous and current coordinates.
        Heading 0 is straight North, PI/2 straight East, PI or -PI straight South, and -PI/2 straight West.
        """

        dx = curr.x - prev.x
        dy = curr.y - prev.y
        angle = math.atan2(dx, dy)
        return angle


    def run_registration(self, source, target, previous_estimated_coordinate, actual_coordinate):

        if self.args.show_debug_visualization:
            source = self.modify_cloud(source, color=[1,0,0])
            self.vis.add_geometry(source, True)
            self.vis.add_geometry(target)
            tqdm.write("Showing source/frame (red) and target/point cloud extract before frame rotation. Press right arrow to continue.")
            self.vis.wait_until_right_arrow_is_pressed()

        self.rotate_frame(source, previous_estimated_coordinate)

        if self.args.show_debug_visualization:
            self.vis.update_geometry(source)
            self.vis.update_geometry(target)
            tqdm.write("Showing source/frame (red) and target/point cloud extract after frame rotation. Press right arrow to continue.")
            self.vis.wait_until_right_arrow_is_pressed()

        self.time("frame rotation")

        # Run the alignment
        iterations = 25
        diffs = []
        transformation_matrix = np.identity(4) if self.previous_matrix is None else self.previous_matrix
        for i in range(10):
            threshold = max(1, 3 - len(diffs))
            reg = self.matcher.match(source, target, trans_init=transformation_matrix, threshold=threshold, max_iterations=iterations)

            # If the calculated transformation matrix is (almost) identical to the one we sent in, we are happy.
            diff = np.abs(np.mean(reg.transformation[0:3, 3]-transformation_matrix[0:3, 3]))
            diffs.append(diff)
            transformation_matrix = reg.transformation
            if diff < 1e-3:
                break

        self.previous_matrix = transformation_matrix

        metadata = {
            "iterations": len(diffs) * iterations,
            "diffs": diffs,
            "frame_ix": actual_coordinate.frame_ix,
            "pcap": self.reader.get_pcap_path()
        }
        self.registration_configs.append(metadata)

        self.check_save_frame_pair(source, target, reg)

        if self.args.show_debug_visualization:
            self.vis.update_geometry(source)
            self.vis.update_geometry(target)
            tqdm.write("Showing source/frame (red) and target/point cloud extract before registration and transformation. Press right arrow to continue.")
            self.vis.wait_until_right_arrow_is_pressed()

            source.transform(transformation_matrix)
            self.vis.update_geometry(source)
            self.vis.update_geometry(target)
            tqdm.write("Showing source/frame (red) and target/point cloud extract after registration and transformation. Press right arrow to continue.")
            self.vis.wait_until_right_arrow_is_pressed()

            self.vis.remove_geometry(source)
            self.vis.remove_geometry(target)

        registration_time = self.time("registration")

        # Extract the translation part from the transformation array
        movement = transformation_matrix[0:3, 3]

        # Now update the current estimate using the single-point cloud's center point
        self.current_estimated_coordinate.translate(movement)

        # Move the cylinder
        self.estimated_position_cylinder.translate(self.current_estimated_coordinate.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)

        # Estimate a new current heading
        self.current_estimated_coordinate.heading = actual_coordinate.heading #self.calculate_heading(previous_estimated_coordinate, self.current_estimated_coordinate)

        # Update the plot with data from this registration
        self.update_plot(reg, registration_time, movement, actual_coordinate)

        tqdm.write(f"[Frame {metadata['frame_ix']}]")
        tqdm.write(f"  Input estimate: {self.to_actual(previous_estimated_coordinate).short_str()}, Output estimate: {self.to_actual(self.current_estimated_coordinate).short_str()}, Actual: {self.to_actual(actual_coordinate).short_str()}")
        tqdm.write(f"  Iterations: {metadata['iterations']}, Final threshold: {threshold}, Final fitness: {reg.fitness:.3f}, Final RMSE: {reg.inlier_rmse:.3f}, Time: {registration_time:.2f}, Movement: {movement[0]:.2f}, {movement[1]:.2f}, {movement[2]:.2f}")
        tqdm.write(f"  Errors :: x: {self.plot.position_error_x[-1]:.2f}, y: {self.plot.position_error_y[-1]:.2f}, z: {self.plot.position_error_z[-1]:.2f}, along: {self.plot.position_error_along_heading[-1]:.2f}, across: {self.plot.position_error_across_heading[-1]:.2f} 2D: {self.plot.position_error_2d[-1]:.2f}, 3D: {self.plot.position_error_3d[-1]:.2f}")
        tqdm.write(f"  Actual heading: {self.get_current_actual_coordinate().heading:.2f}, estimated heading: {self.current_estimated_coordinate.heading:.2f}")

        # Append the new movement to the path
        self.movement_path.points.append(self.current_estimated_coordinate.np())

        # Add the new line
        if len(self.movements) == 2:
            if self.preview_always:
                self.vis.add_geometry(self.movement_path)
        if len(self.movements) >= 2:
            self.movement_path.lines.append([len(self.movements) - 2, len(self.movements) - 1])
            self.movement_path.paint_uniform_color([1, 0, 0])
            if self.preview_always:
                self.vis.update_geometry(self.movement_path)

        self.time("book keeping")

        return reg

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
    def save_data(path, data, pretty):

        with open(path, 'w') as f:
            if pretty:
                json.dump(data, f, indent=4)
            else:
                json.dump(data, f, indent=None, separators=(',', ':'))

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
        self.vis = Open3DVisualizer(add_axes=False, window_name=self.visualization_window_name)

        if self.preview_always:

            # Initiate non-blocking visualizer window
            self.vis.refresh_non_blocking()

            # Show the first frame and reset the view
            if self.merged_frame is not None:
                self.vis.show_frame(self.merged_frame)

            if self.skip_until_circle_center_cylinder is not None:
                self.vis.add_geometry(self.skip_until_circle_center_cylinder)
            if self.run_until_circle_center_cylinder is not None:
                self.vis.add_geometry(self.run_until_circle_center_cylinder)
            
            self.vis.set_follow_vehicle_view()

            if self.actual_movement_path is not None:
                self.vis.add_geometry(self.actual_movement_path, True)
            
            self.vis.add_geometry(self.actual_position_cylinder)
            self.vis.add_geometry(self.estimated_position_cylinder)
            self.vis.add_geometry(self.start_position_cylinder)

            self.check_save_screenshot(0, True)

        self.plot = Plotter(self.preview_always)

        # Add the first coordinates to the lists
        self.estimated_coordinates.append(self.current_estimated_coordinate.clone())
        self.actual_coordinates.append(self.initial_coordinate.clone())

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

        if self.current_estimated_coordinate is not None:

            # Add the current coordinate to the list of estimations
            self.estimated_coordinates.append(self.current_estimated_coordinate.clone())
            self.actual_coordinates.append(actual_coordinate.clone())

            # Calculate differences between the estimate and the actual coordinate
            dx = abs(self.current_estimated_coordinate.x - actual_coordinate.x)
            dy = abs(self.current_estimated_coordinate.y - actual_coordinate.y)
            dz = self.current_estimated_coordinate.alt - actual_coordinate.alt

            # Calculate distances along and across of the movement vector (heading)
            dist = self.calculate_distance_between_points(self.current_estimated_coordinate.x, self.current_estimated_coordinate.y, actual_coordinate.x, actual_coordinate.y, actual_coordinate.heading)

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

        processed_frames = len(self.movements)
        if processed_frames == 1 and self.args.save_after_first_frame:
            self.check_results_saving()
        elif self.args.save_after_frames > 0 and processed_frames % self.args.save_after_frames == 0:
            self.check_results_saving()

        if self.args.raise_on_2d_error > 0 and self.plot.position_error_2d[-1] > self.args.raise_on_2d_error:
            raise Exception("The navigation error (" + str(self.plot.position_error_3d[-1]) + ") is larger than the given limit (--raise-on-2d-error " + str(self.args.raise_on_2d_error) + ").")

        if self.args.raise_on_3d_error > 0 and self.plot.position_error_3d[-1] > self.args.raise_on_3d_error:
            raise Exception("The navigation error (" + str(self.plot.position_error_3d[-1]) + ") is larger than the given limit (--raise-on-3d-error " + str(self.args.raise_on_3d_error) + ").")

        if self.args.raise_on_movement > 0 and self.plot.distances[-1] > self.args.raise_on_movement:
            raise Exception("The movement between the last two frames (" + str(self.plot.distances[-1]) + ") was larger than the given limit (--raise-on-movement " + str(self.args.raise_on_movement) + ").")           

    def check_results_saving(self, save_cloud=False, exception=None, finished=False):

        results = self.get_results()
        
        results["initial_coordinate"] = self.initial_coordinate.json(True)
        results["current_estimated_coordinate"] = self.current_estimated_coordinate.json()
        results["estimated_coordinates"] = [x.json() for x in self.estimated_coordinates]
        results["actual_coordinates"] = [x.json(True) for x in self.actual_coordinates]
        results["registration_configs"] = self.registration_configs
        results["point_cloud_offset"] = self.full_point_cloud_offset.tolist()

        status = "ongoing"
        if finished:
            status = "finished"
        if exception is not None:
            status = "failed"
            results["fatal_exception"] = str(exception)
        results["status"] = status

        results["args"] = vars(self.args)
        
        if self.save_path is not None:

            self.ensure_dir(os.path.join(self.save_path, "plot.png"))
            self.plot.save_plot(os.path.join(self.save_path, "plot.png"))

            if save_cloud and self.build_cloud:
                try:
                    self.save_cloud_as_las(os.path.join(self.save_path, "cloud.laz"), self.merged_frame)
                    o3d.io.write_point_cloud(os.path.join(self.save_path, "cloud.pcd"), self.merged_frame, compressed=True)
                except:
                    tqdm.write("Failed to save point cloud.")

            self.time("results saving")
            
            self.save_data(os.path.join(self.save_path, "data.json"), results, self.args.save_pretty_json)

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
        if self.has_waited or self.wait_after_first_frame <= 0:
            return

        end_at = time.time() + self.wait_after_first_frame
        with tqdm(desc="Waiting for vis. adjustment", total=self.wait_after_first_frame, leave=False, **self.tqdm_config) as pbar:
            while time.time() < end_at:
                self.vis.refresh_non_blocking()
                pbar.n = int(self.wait_after_first_frame - end_at + time.time())
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
    def load_arguments_from_json(parser, args, json_path):

        # Extract the keys for all arguments
        arg_keys = vars(args)

        # Extract all defaults values.
        # In order to do this, we fake parsing a list of empty arguments.
        # But since some arguments are required, we must provide dummy values for those.
        required_arguments = ["--pcap", "x", "--sbet", "x"]
        if "point_cloud" in [x.dest for x in parser._actions]:
            required_arguments.append("--point-cloud")
            required_arguments.append("x")
        defaults = vars(parser.parse_args(required_arguments))

        # Load the given JSON file
        with open(json_path) as f:
            data = json.load(f)

            # Go through each defined key in the JSON file
            for key in data:

                # Allow prefixing keys with # to ignore them
                if key.startswith("#"):
                    continue 
                    
                arg_key = key.replace("--", "").replace("-", "_")

                # Ignore absoluteNavigator arguments to allow common .json file
                if arg_key in ["point_cloud", "hide_point_cloud", "cloud_part_radius"]:
                    continue

                if not arg_key in arg_keys:
                    raise Exception("Unrecognized agrument in the JSON file (--load-arguments): " + key + " (" + arg_key + ")")

                value = getattr(args, arg_key, None)
                is_default = value == defaults[arg_key]
                if value is None or value == "[load]" or is_default or arg_keys[arg_key] == False:
                    setattr(args, arg_key, data[key])

    @staticmethod
    def add_standard_and_parse_args(parser):
        parser.add_argument('--algorithm', type=str, default="NICP", required=False, help="Use this registration algorithm (see names in algorithmHelper.py).")
        parser.add_argument('--use-actual-coordinate', dest='use_actual_coordinate', default=False, action='store_true', help="If set to true, the actual coordinate will be used as input for the registration instead of the estimated coordinate.")
        
        parser.add_argument('--skip-last-frame-in-pcap-file', type=bool, default=True, required=False, help="The last frame in each PCAP file is often corrupted. This flag makes the pcap reader skip the last frame in each file.")
        parser.add_argument('--build-cloud-after', type=int, default=1, required=False, help="How often registered frames should be added to the generated point cloud. 0 or lower deactivates the generated point cloud. 1 or higher generates a point cloud with details (and time usage) decreasing with higher numbers.")
        parser.add_argument('--voxel-size', type=float, default=0.1, required=False, help="The voxel size used for cloud downsampling. If less than or equal to zero, downsampling will be disabled.")
        parser.add_argument('--downsample-after', type=int, default=10, required=False, help="The cloud will be downsampled (which is an expensive operation for large clouds, so don't do it too often) after this many registered frames have been added. If this number is higher than the number of frames being read, it will be downsampled once at the end of the process (unless downsampling is disabled, see --voxel-size).")
        parser.add_argument('--wait-after-first-frame', type=int, default=0, required=False, help="If given, the analysis will wait for this many seconds after the first frame to allow the visualization to be manually adjusted (zooming, panning, etc).")
        parser.add_argument('--preview', type=str, default="always", choices=['always', 'end', 'never'], help="Show constantly updated point cloud and data plot previews while processing ('always'), show them only at the end ('end'), or don't show them at all ('never').")
        parser.add_argument('--show-debug-visualization', dest='show_debug_visualization', default=False, action='store_true', help="If set to true, the analysis will pause multiple times during each frame to show the different steps in the visualizer (zoom out and find the origin, that's where stuff happens).")
        parser.add_argument('--visualization-window-name', type=str, default=None, required=False, help="If set, the visualization window will have this title. If not set, the title will be based on the pcap file/folder path.")

        parser.add_argument('--skip-start', type=int, default=0, required=False, help="If given a positive number larger than 0, this many frames will be skipped before starting processing frames.")
        parser.add_argument('--skip-every-frame', type=int, default=0, required=False, help="If given a positive number larger than 0, this many frames will be skipped between every frame read from the PCAP file.")
        
        parser.add_argument('--skip-until-radius', type=int, default=20, required=False, help="If given together with --skip-until-x and --skip-until-y, the analysis will skip frames until the actual position enters the circle given by these three parameters.")
        parser.add_argument('--skip-until-x', type=float, default=None, required=False, help="If given together with --skip-until-x and --skip-until-radius, the analysis will skip frames until the actual position enters the circle given by these three parameters.")
        parser.add_argument('--skip-until-y', type=float, default=None, required=False, help="If given together with --skip-until-y and --skip-until-radius, the analysis will skip frames until the actual position enters the circle given by these three parameters.")
        
        parser.add_argument('--run-until-radius', type=int, default=20, required=False, help="If given together with --run-until-x and --run-until-y, the analysis will run frames until the actual position enters the circle given by these three parameters.")
        parser.add_argument('--run-until-x', type=float, default=None, required=False, help="If given together with --run-until-x and --run-until-radius, the analysis will run frames until the actual position enters the circle given by these three parameters.")
        parser.add_argument('--run-until-y', type=float, default=None, required=False, help="If given together with --run-until-y and --run-until-radius, the analysis will run frames until the actual position enters the circle given by these three parameters.")
        
        parser.add_argument('--frames', type=int, default=-1, required=False, help="If given a number larger than 1, only this many frames will be processed before the analysis is stopped (useful for shorter test runs).")
        
        parser.add_argument('--save-to', type=str, default=None, required=False, help="If given, final results will be stored in this folder.")
        parser.add_argument('--save-pretty-json', action="store_true", help="Results will normally be saved as minified JSON (without whitespace) to save space, but this argument can be used to write pretty (human readable) JSON instead.")
        parser.add_argument('--save-after-first-frame', action="store_true", help="Results will be stored after the first frame (useful to see that the output is correct before running a long analysis).")
        parser.add_argument('--save-after-frames', type=int, default=0, required=False, help="If given, results will be saved after every nth frame (useful to keep an eye on results during a long analysis).")
        parser.add_argument('--save-screenshots-to', type=str, default=None, required=False, help="If given, point cloud screenshots will be saved in this directory with their indices as filenames (0.png, 1.png, 2.png, etc). Only works if --preview is set to 'always'.")
        parser.add_argument('--save-frame-pairs-to', type=str, default=None, required=False, help="If given, frame pairs with a registered fitness below --save-frame-pair-threshold will be saved to the given directory for manual inspection.")
        parser.add_argument('--save-frame-pair-threshold', type=float, default=0.97, required=False, help="If --save-frame-pairs-to is given, frame pairs with a registered fitness value below this value will be saved.")
        
        parser.add_argument('--raise-on-2d-error', type=float, default=50, required=False, help="The frame processing will raise an exception if the 2d distance between the actual and the estimated position is larger than this number. Set to 0 or lower to deactivate.")
        parser.add_argument('--raise-on-3d-error', type=float, default=50, required=False, help="The frame processing will raise an exception if the 3d distance between the actual and the estimated position is larger than this number. Set to 0 or lower to deactivate.")
        parser.add_argument('--raise-on-movement', type=float, default=100, required=False, help="The frame processing will raise an exception if the distance between two last estimated positions is larger than this number. Set to 0 or lower to deactivate.")
        
        parser.add_argument('--load-arguments', type=str, default=None, required=False, help="Additional arguments will be loaded from the given json file. Arguments already set from the command line will not be overwritten.")

        args = parser.parse_args()

        if args.load_arguments is not None:
            NavigatorBase.load_arguments_from_json(parser, args, args.load_arguments)

        if args.save_screenshots_to is not None and args.preview != "always":
            raise ValueError("Cannot save cloud screenshots without --preview being set to 'always'.")

        tqdm.write("Running analysis with arguments:")
        tqdm.write(json.dumps(vars(args), indent=4, sort_keys=True))

        return args