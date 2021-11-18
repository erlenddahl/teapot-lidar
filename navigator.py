from pcapReader import PcapReader
from open3dVisualizer import Open3DVisualizer
from plotter import Plotter
import numpy as np
import time
import open3d as o3d

from matchers.nicp import NicpMatcher

class LidarNavigator:

    def __init__(self, pcapPath, metaDataPath):
        """Initialize a LidarNavigator by reading metadata and setting
        up a package source from the pcap file.
        """

        self.reader = PcapReader(pcapPath, metaDataPath)

        # Fetch the first frame and use it as a base for the generated visualization
        self.voxel_size = 0.1

        self.matcher = NicpMatcher()

    def navigateThroughFile(self):
        """ Runs through each frame in the file. For each pair of frames, use NICP
        to align the frames, then merge them and downsample the result. The transformation
        matrix from the NICP operation is used to calculate the movement of the center point
        (the vehicle) between the frames. Each movement is stored, and drawn as a red line
        to show the driving route.
        """
        
        # Initialize the visualizer
        self.vis = Open3DVisualizer()
        self.vis.refresh_non_blocking()

        # Initialize the list of movements as well as the merged frame, and the first 
        # source frame.
        self.movements = []
        self.mergedFrame = self.reader.readFrameAsPointCloud(0, True)
        self.previousFrame = self.reader.readFrameAsPointCloud(0, True)

        # Estimate normals for the first source frame in order to speed up the 
        # alignment operation.
        self.previousFrame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        # Show the first frame and reset the view
        self.vis.showFrame(self.mergedFrame)
        self.vis.reset_view()

        plot = Plotter()

        # Enumerate all frames until the end of the file and run the merge operation.
        while self.mergeNextFrame(plot):

            # Refresh the non-blocking visualization
            self.vis.refresh_non_blocking()

            plot.update()

        # When everything is finished, print a summary, and continue showing the
        # visualization in a blocking way until the user stops it.
        plot.print_summary()
        self.vis.run()

    def alignFrame(self, source, target):
        """ Aligns the target frame with the source frame using the selected algorithm.
        """

        # Estimate normals for the target frame (the source frame will always have
        # normals from the previous step).
        print("Estimating normals")
        target.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        # Run the selected registration algorithm
        reg = self.matcher.match(source, target)

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
        frame = self.reader.nextFrameAsPointCloud(True)

        # If it is empty, that (usually) means we have reached the end of
        # the file. Return False to stop the loop.
        if frame is None:
            return False

        # Run the alignment
        startTime = time.perf_counter()
        
        transformation, movement, reg = self.alignFrame(self.previousFrame, frame)
        
        plot.timeUsages.append(time.perf_counter() - startTime)
        plot.rmses.append(reg.inlier_rmse)
        plot.fitnesses.append(reg.fitness)
        plot.distances.append(np.sqrt(np.dot(movement,movement)))

        # Transform earlier points so that they follow the ongoing model transformation
        for i,m in enumerate(self.movements):
            self.movements[i] = m + movement

        # Append the newest movement
        self.movements.append(movement)

        # Remove the old line (if any)
        if len(self.movements) > 2:
            self.vis.remove_geometry(self.movementPath)

        # Generate a new line
        points = o3d.utility.Vector3dVector(self.movements)
        lines = o3d.utility.Vector2iVector([[i, i + 1] for i in range(len(points) - 1)])

        self.movementPath = o3d.geometry.LineSet(
            points=points, lines=lines
        )
        self.movementPath.colors = o3d.utility.Vector3dVector([[1, 0, 0] for _ in range(len(points))])

        # Add the new line
        if len(self.movements) >= 2:
            self.movementPath.paint_uniform_color([1, 0, 0])
            self.vis.add_geometry(self.movementPath)

        print("Merging and downsampling full 3D model")
        startTime = time.perf_counter()

        # Transform the merged visualization to fit the next frame
        merged = self.mergedFrame.transform(transformation)

        # Combine the points from the merged visualization with the points from the next frame
        merged += frame

        # Downsample the merged visualization to make it faster to work with.
        # Otherwise it would grow extremely large, as it would contain all points
        # from all processed point clouds.
        self.mergedFrame = merged.voxel_down_sample(voxel_size=self.voxel_size)
        print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

        # Store this frame so that it can be used as the source frame in the next iteration.
        self.previousFrame = frame

        # Update the visualization
        self.vis.showFrame(self.mergedFrame, True)

        # Return True to let the loop continue to the next frame.
        return True
        

if __name__ == "__main__":

    args = PcapReader.getPathArgs()

    # Create and start a visualization
    navigator = LidarNavigator(args.pcap, args.json)
    navigator.navigateThroughFile()