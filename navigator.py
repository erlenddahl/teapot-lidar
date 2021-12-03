from pcapReader import PcapReader
from open3dVisualizer import Open3DVisualizer
from plotter import Plotter
import numpy as np
import os
from tqdm import tqdm
import open3d as o3d
import laspy
from datetime import datetime
import json
import argparse
from taskTimer import TaskTimer

from matchers.nicp import NicpMatcher
from matchers.downsamplefirst import DownsampleFirstNicpMatcher
from matchers.globalregistrationfirst import GlobalFirstNicpMatcher
from matchers.fastglobalregistrationfirst import FastGlobalFirstNicpMatcher

class LidarNavigator:

    def __init__(self, pcap_paths, meta_data_paths, frames = -1, skip_frames = 0, voxel_size = 0.1, downsample_cloud_after_frames = 10, preview = "always", save_path = None, save_screenshots_to = None, save_frame_pairs_to = None, save_frame_pair_threshold = 0.97):
        """Initialize a LidarNavigator by reading metadata and setting
        up a package source from the pcap file.
        """

        self.timer = TaskTimer()

        print("Preparing ...")

        self.reader = PcapReader.from_lists(pcap_paths, meta_data_paths, skip_frames)

        # Fetch the first frame and use it as a base for the generated visualization
        self.voxel_size = voxel_size

        self.matcher = NicpMatcher()
        self.frame_limit = frames
        self.preview_always = preview == "always"
        self.preview_at_end = preview == "always" or preview =="end"
        self.save_path = save_path
        self.downsample_timer = downsample_cloud_after_frames
        self.downsample_cloud_after_frames = downsample_cloud_after_frames
        self.merged_frame_is_dirty = True
        self.save_screenshots_to = save_screenshots_to
        self.save_frame_pairs_to = save_frame_pairs_to
        self.save_frame_pair_threshold = save_frame_pair_threshold
        
        self.time("setup")

        if self.frame_limit <= 1:
            self.frame_limit = self.reader.count_frames()
            self.time("frame counting")

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

    def navigate_through_file(self):
        """ Runs through each frame in the file. For each pair of frames, use NICP
        to align the frames, then merge them and downsample the result. The transformation
        matrix from the NICP operation is used to calculate the movement of the center point
        (the vehicle) between the frames. Each movement is stored, and drawn as a red line
        to show the driving route.
        """
        
        self.timer.reset()

        # Initialize the list of movements as well as the merged frame, and the first 
        # source frame.
        self.movements = []

        self.movement_path = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector([]), lines=o3d.utility.Vector2iVector([])
        )

        self.merged_frame = self.reader.next_frame(True, self.timer)
        self.previous_frame = self.merged_frame

        # Estimate normals for the first source frame in order to speed up the 
        # alignment operation.
        self.previous_frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        # Initialize the visualizer
        self.vis = Open3DVisualizer()

        if self.preview_always:
            # Initiate non-blocking visualizer window
            self.vis.refresh_non_blocking()

            # Show the first frame and reset the view
            self.vis.show_frame(self.merged_frame)
            self.vis.reset_view()

            self.check_save_screenshot(0, True)

        plot = Plotter(self.preview_always)

        self.time("navigation preparations")

        # Enumerate all frames until the end of the file and run the merge operation.
        for i in tqdm(range(1, self.frame_limit), total=self.frame_limit, ascii=True, initial=1):
            
            try:

                if self.merge_next_frame(plot): 

                    # Refresh the non-blocking visualization
                    if self.preview_always:
                        self.vis.refresh_non_blocking()
                        self.time("visualization refresh")

                        self.check_save_screenshot(i)

                    plot.step(self.preview_always)
                    self.time("plot step")

            except KeyboardInterrupt:
                
                print("")
                print("********************************")
                print("Process aborted. Results so far:")
                print("********************************")
                plot.print_summary(self.timer)
                print("")
                print("")

                raise

        # Ensure the final cloud has been downsampled
        self.ensure_merged_frame_is_downsampled()

        # When everything is finished, print a summary, and save the point cloud and debug data.
        if self.preview_at_end:
            plot.update()

        if self.save_path is not None:
            filenameBase = self.save_path.replace("[time]", datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f%z'))
            filenameBase = filenameBase.replace("[pcap]", os.path.basename(self.reader.pcap_path).replace(".pcap", ""))
            self.ensure_dir(filenameBase)
            plot.save_plot(filenameBase + "_plot.png")
            self.save_cloud_as_las(filenameBase + "_cloud.laz", self.merged_frame)
            o3d.io.write_point_cloud(filenameBase + "_cloud.pcd", self.merged_frame, compressed=True)

            self.time("results saving")
            
            self.save_data(filenameBase + "_data.json", plot)
        
        plot.print_summary(self.timer)

        # Then continue showing the visualization in a blocking way until the user stops it.
        if self.preview_at_end:
            self.vis.show_frame(self.merged_frame)
            self.vis.remove_geometry(self.movement_path)
            self.vis.add_geometry(self.movement_path)
            self.vis.reset_view()

            self.vis.run()

    def ensure_merged_frame_is_downsampled(self):

        if self.voxel_size <= 0:
            return

        if not self.merged_frame_is_dirty:
            return

        self.merged_frame = self.merged_frame.voxel_down_sample(voxel_size=self.voxel_size)
        self.merged_frame_is_dirty = False
        self.time("cloud downsampling")

    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if len(directory) < 1: 
            return
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_data(self, path, plot):

        data = plot.get_json(self.timer)

        data["movement"] = np.asarray(self.movement_path.points).tolist()

        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def save_cloud_as_las(self, path, cloud):

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

    def merge_next_frame(self, plot):
        """ Reads the next frame, aligns it with the previous frame, merges them together
        to create a 3D model, and tracks the movement between frames.
        """

        # Fetch the next frame
        frame = self.reader.next_frame(True, self.timer)

        # If it is empty, that (usually) means we have reached the end of
        # the file. Return False to stop the loop.
        if frame is None:
            return False

        # Estimate normals for the target frame (the source frame will always have
        # normals from the previous step).
        frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("normal estimation")

        # Run the alignment
        reg = self.matcher.match(self.previous_frame, frame)
        self.check_save_frame_pair(self.previous_frame, frame, reg)

        registration_time = self.time("registration")

        # Calculate how much the center point has moved by transforming [0,0,0] with
        # the calculated transformation
        movement = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(reg.transformation).get_center()
        
        plot.timeUsages.append(registration_time)
        plot.rmses.append(reg.inlier_rmse)
        plot.fitnesses.append(reg.fitness)
        plot.distances.append(np.sqrt(np.dot(movement, movement)))

        # Append the newest movement
        self.movements.append(movement)

        # Append the new movement to the path
        self.movement_path.points.append([0,0,0])
        self.movement_path = self.movement_path.transform(reg.transformation)

        # Add the new line
        if len(self.movements) == 2:
            self.vis.add_geometry(self.movement_path)
        if len(self.movements) >= 2:
            self.movement_path.lines.append([len(self.movements) - 2, len(self.movements) - 1])
            self.movement_path.paint_uniform_color([1, 0, 0])
            self.vis.update_geometry(self.movement_path)

        self.time("book keeping")

        # Transform the frame to fit the merged point cloud
        self.merged_frame = self.merged_frame.transform(reg.transformation)

        self.time("frame transformation")

        # Combine the points from the merged visualization with the points from the next frame
        self.merged_frame += frame
        self.merged_frame_is_dirty = True

        self.time("cloud merging")

        # Downsample the merged visualization to make it faster to work with.
        # Otherwise it would grow extremely large, as it would contain all points
        # from all processed point clouds.
        # Don't do this on every frame, as it takes a lot of time.
        self.downsample_timer -= 1
        if self.downsample_timer <= 0:
            self.ensure_merged_frame_is_downsampled()
            self.downsample_timer = self.downsample_cloud_after_frames

        # Store this frame so that it can be used as the source frame in the next iteration.
        self.previous_frame = frame

        # Update the visualization
        if self.preview_always:
            self.vis.show_frame(self.merged_frame, True)

            self.time("visualization")

        # Return True to let the loop continue to the next frame.
        return True
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    PcapReader.add_path_arguments(parser)
    parser.add_argument('--frames', type=int, default=-1, required=False, help="If given a number larger than 1, only this many frames will be read from the PCAP file.")
    parser.add_argument('--skip-frames', type=int, default=0, required=False, help="If given a positive number larger than 0, this many frames will be skipped between every frame read from the PCAP file.")
    parser.add_argument('--voxel-size', type=float, default=0.1, required=False, help="The voxel size used for cloud downsampling. If less than or equal to zero, downsampling will be disabled.")
    parser.add_argument('--downsample-after', type=int, default=25, required=False, help="The cloud will be downsampled after this many frames (which is an expensive operation for large clouds, so don't do it too often). If this number is higher than the number of frames being read, it will be downsampled once at the end of the process (unless downsampling is disabled, see --voxel-size).")
    parser.add_argument('--preview', type=str, default="always", choices=['always', 'end', 'never'], help="Show constantly updated point cloud and data plot previews while processing ('always'), show them only at the end ('end'), or don't show them at all ('never').")
    parser.add_argument('--save-to', type=str, default=None, required=False, help="If given, final results will be stored at this path. The path will be used for all types of results, with appendices depending on file type ('_data.json', '_plot.png', '_cloud.laz', '_cloud.pcd'). The path can include \"[pcap]\" and/or \"[time]\" which will be replaced with the name of the parsed PCAP file and the time of completion respectively.")
    parser.add_argument('--save-screenshots-to', type=str, default=None, required=False, help="If given, point cloud screenshots will be saved in this directory with their indices as filenames (0.png, 1.png, 2.png, etc). Only works if --preview is set to 'always'.")
    parser.add_argument('--save-frame-pairs-to', type=str, default=None, required=False, help="If given, frame pairs with a registered fitness below --save-frame-pair-threshold will be saved to the given directory for manual inspection.")
    parser.add_argument('--save-frame-pair-threshold', type=float, default=0.97, required=False, help="If --save-frame-pairs-to is given, frame pairs with a registered fitness value below this value will be saved.")

    args = parser.parse_args()

    if args.save_screenshots_to is not None and args.preview != "always":
        raise ValueError("Cannot save cloud screenshots without --preview being set to 'always'.")

    # Create and start a visualization
    navigator = LidarNavigator(args.pcap, args.json, args.frames, args.skip_frames, args.voxel_size, args.downsample_after, args.preview, args.save_to, args.save_screenshots_to, args.save_frame_pairs_to, args.save_frame_pair_threshold)
    navigator.navigate_through_file()