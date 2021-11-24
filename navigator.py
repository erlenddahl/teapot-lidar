from pcapReader import PcapReader
from open3dVisualizer import Open3DVisualizer
from plotter import Plotter
import numpy as np
import os
import time
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

    def __init__(self, pcapPath, metaDataPath, frames = -1, nth_frame = 0, downsample_cloud_after_frames = 10, preview = "always", save_path = None):
        """Initialize a LidarNavigator by reading metadata and setting
        up a package source from the pcap file.
        """

        self.timer = TaskTimer()

        print("Preparing ...")

        self.reader = PcapReader(pcapPath, metaDataPath, nth_frame)

        # Fetch the first frame and use it as a base for the generated visualization
        self.voxel_size = 0.1

        self.matcher = NicpMatcher()
        self.frame_limit = frames
        self.previewAlways = preview == "always"
        self.previewAtEnd = preview == "always" or preview =="end"
        self.save_path = save_path
        self.downsample_timer = downsample_cloud_after_frames
        self.downsample_cloud_after_frames = downsample_cloud_after_frames
        
        self.time("setup")

        if self.frame_limit <= 1:
            self.frame_limit = self.reader.count_frames()
            self.time("frame counting")

    def time(self, key):
        self.timer.time(key)

    def navigateThroughFile(self):
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

        self.movementPath = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector([]), lines=o3d.utility.Vector2iVector([])
        )

        self.mergedFrame = self.reader.nextFrame(True, self.timer)
        self.previousFrame = self.mergedFrame

        # Estimate normals for the first source frame in order to speed up the 
        # alignment operation.
        self.previousFrame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        # Initialize the visualizer
        self.vis = Open3DVisualizer()

        if self.previewAlways:
            # Initiate non-blocking visualizer window
            self.vis.refresh_non_blocking()

            # Show the first frame and reset the view
            self.vis.showFrame(self.mergedFrame)
            self.vis.reset_view()

        plot = Plotter(self.previewAlways)

        self.time("navigation preparations")

        # Enumerate all frames until the end of the file and run the merge operation.
        for _ in tqdm(range(1, self.frame_limit), total=self.frame_limit, ascii=True, initial=1):
            
            try:

                if self.mergeNextFrame(plot): 

                    # Refresh the non-blocking visualization
                    if self.previewAlways:
                        self.vis.refresh_non_blocking()
                        self.time("visualization refresh")

                    plot.step(self.previewAlways)
                    self.time("plot step")

            except KeyboardInterrupt:
                print("Process aborted. Results so far:")
                plot.print_summary(self.timer)
                raise

        # When everything is finished, print a summary, and save the point cloud and debug data.
        if self.previewAtEnd:
            plot.update()
        plot.print_summary(self.timer)

        if self.save_path is not None:
            filenameBase = self.save_path.replace("[time]", datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f%z'))
            filenameBase = filenameBase.replace("[pcap]", self.reader.pcapPath.replace(".pcap", ""))
            self.ensure_dir(filenameBase)
            self.save_data(filenameBase + "_data.json", plot)
            plot.save_plot(filenameBase + "_plot.png")
            self.save_cloud(filenameBase + "_cloud.laz", self.mergedFrame)

            self.time("results saving")

        # Then continue showing the visualization in a blocking way until the user stops it.
        if self.previewAtEnd:
            self.vis.showFrame(self.mergedFrame)
            self.vis.reset_view()

            self.vis.run()

    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if len(directory) < 1: 
            return
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_data(self, path, plot):

        data = plot.get_json(self.timer)

        data["movement"] = np.asarray(self.movementPath.points).tolist()

        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def save_cloud(self, path, cloud):

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

    def alignFrame(self, source, target):
        """ Aligns the target frame with the source frame using the selected algorithm.
        """

        # Estimate normals for the target frame (the source frame will always have
        # normals from the previous step).
        target.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("normal estimation")

        # Run the selected registration algorithm
        reg = self.matcher.match(source, target)

        self.time("registration")

        # Calculate how much the center point has moved by transforming [0,0,0] with
        # the calculated transformation
        movement = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(reg.transformation).get_center()
        
        # Return the transformation and the movement
        return reg.transformation, movement, reg

    def mergeNextFrame(self, plot):
        """ Reads the next frame, aligns it with the previous frame, merges them together
        to create a 3D model, and tracks the movement between frames.
        """

        # Fetch the next frame
        frame = self.reader.nextFrame(True, self.timer)

        # If it is empty, that (usually) means we have reached the end of
        # the file. Return False to stop the loop.
        if frame is None:
            return False

        startTime = time.perf_counter()
        
        # Run the alignment
        transformation, movement, reg = self.alignFrame(self.previousFrame, frame)
        
        plot.timeUsages.append(time.perf_counter() - startTime)
        plot.rmses.append(reg.inlier_rmse)
        plot.fitnesses.append(reg.fitness)
        plot.distances.append(np.sqrt(np.dot(movement,movement)))

        # Append the newest movement
        self.movements.append(movement)

        # Append the new movement to the path
        self.movementPath.points.append([0,0,0])
        self.movementPath = self.movementPath.transform(transformation)

        # Add the new line
        if len(self.movements) == 2:
            self.vis.add_geometry(self.movementPath)
        if len(self.movements) >= 2:
            self.movementPath.lines.append([len(self.movements) - 2, len(self.movements) - 1])
            self.movementPath.paint_uniform_color([1, 0, 0])
            self.vis.update_geometry(self.movementPath)

        self.time("book keeping")

        # Transform the merged visualization to fit the next frame
        merged = self.mergedFrame.transform(transformation)

        self.time("frame transformation")

        # Combine the points from the merged visualization with the points from the next frame
        downsampled_frame = frame.voxel_down_sample(voxel_size=self.voxel_size)

        self.time("frame downsampling")

        merged += downsampled_frame

        self.time("cloud merging")

        # Downsample the merged visualization to make it faster to work with.
        # Otherwise it would grow extremely large, as it would contain all points
        # from all processed point clouds.
        # Don't do this on every frame, as it takes a lot of time.
        self.downsample_timer -= 1
        if self.downsample_timer <= 0:
            merged = merged.voxel_down_sample(voxel_size=self.voxel_size)
            self.time("cloud downsampling")
            self.downsample_timer = self.downsample_cloud_after_frames
        
        self.mergedFrame = merged

        # Store this frame so that it can be used as the source frame in the next iteration.
        self.previousFrame = frame

        # Update the visualization
        if self.previewAlways:
            self.vis.showFrame(self.mergedFrame, True)

            self.time("visualization")

        # Return True to let the loop continue to the next frame.
        return True
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    PcapReader.add_path_arguments(parser)
    parser.add_argument('--frames', type=int, default=-1, required=False, help="If given a number larger than 1, only this many frames will be read from the PCAP file.")
    parser.add_argument('--skip-frames', type=int, default=0, required=False, help="If given a positive number larger than 0, this many frames will be skipped between every frame read from the PCAP file.")
    parser.add_argument('--downsample-after', type=int, default=10, required=False, help="The cloud will be downsampled after this many frames (which is an expensive operation for large clouds, so don't do it too often).")
    parser.add_argument('--preview', type=str, default="always", choices=['always', 'end', 'never'], help="Show constantly updated point cloud and data plot previews while processing ('always'), show them only at the end ('end'), or don't show them at all ('never').")
    parser.add_argument('--save-to', type=str, default=None, required=False, help="If given, final results will be stored at this path. The path will be used for all types of results, with appendices depending on file type ('_data.json', '_plot.png', '_cloud.laz'). The path can include \"[pcap]\" and/or \"[time]\" which will be replaced with the name of the parsed PCAP file and the time of completion respectively.")
    
    args = parser.parse_args()

    # Create and start a visualization
    navigator = LidarNavigator(args.pcap, args.json, args.frames, args.skip_frames, args.downsample_after, args.preview, args.save_to)
    navigator.navigateThroughFile()