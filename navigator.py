from pcapReader import PcapReader
from open3dVisualizer import Open3DVisualizer
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time
import math
import open3d as o3d

class LidarNavigator:

    def __init__(self, pcapPath, metaDataPath):
        """Initialize a LidarNavigator by reading metadata and setting
        up a package source from the pcap file.
        """

        self.reader = PcapReader(pcapPath, metaDataPath)

        # Fetch the first frame and use it as a base for the generated visualization
        self.voxel_size = 0.1

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
        self.distances = []
        self.timeUsages = []
        self.rmses = []
        self.fitnesses = []
        self.mergedFrame = self.reader.readFrameAsPointCloud(0, True)
        self.previousFrame = self.reader.readFrameAsPointCloud(0, True)

        # Estimate normals for the first source frame in order to speed up the 
        # alignment operation.
        self.previousFrame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        # Show the first frame and reset the view
        self.vis.showFrame(self.mergedFrame)
        self.vis.reset_view()

        # Enable interactive mode, which redraws plot on change
        plt.ion()

        # Initialize plot
        plot_x = []

        # Show the plot without blocking
        plt.show(block=False)
        fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False)

        # Enumerate all frames until the end of the file and run the merge operation.
        while self.mergeNextFrame():

            # Refresh the non-blocking visualization
            self.vis.refresh_non_blocking()

            plot_x.append(len(self.movements) - 1)

            ax1.clear()
            ax2.clear()
            ax3.clear()

            ax1.plot(plot_x, self.timeUsages, color="blue", label="calculation time")
            ax2.plot(plot_x, self.distances, color="red", label="distance")
            ax3.plot(plot_x, self.rmses, color="purple", label="rmse")
            ax3.plot(plot_x, self.fitnesses, color="green", label="fitness")
            
            ax1.set_ylabel("Seconds")
            ax2.set_ylabel("Meters")
            ax3.set_xlabel("Frame index")

            handles1, labels1 = ax1.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            handles3, labels3 = ax3.get_legend_handles_labels()
            fig.legend(handles1+handles2+handles3, labels1+labels2+labels3, loc='center right')

        # When everything is finished, continue showing the visualization
        # in a blocking way.
        self.vis.run()

    def alignFrame(self, source, target):
        """ Aligns the target frame with the source frame using NICP.
        """

        # Initialize an initial transformation. This is meant to be a
        # rough transformation to align the frames, but as lidar frames
        # are roughly aligned anyway, we use the identity matrix.
        trans_init = np.identity(4)

        # Estimate normals for the target frame (the source frame will always have
        # normals from the previous step).
        print("Estimating normals")
        target.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        # Run NICP
        print("Performing point-to-plane registration")
        threshold = 1
        reg_p2l = o3d.pipelines.registration.registration_icp(
            source, target, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))

        # Calculate how much the center point has moved by transforming [0,0,0] with
        # the calculated transformation
        movement = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(reg_p2l.transformation).get_center()
        
        # Return the transformation and the movement
        return reg_p2l.transformation, movement, reg_p2l

    def mergeNextFrame(self):
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
        
        self.timeUsages.append(time.perf_counter() - startTime)
        self.rmses.append(reg.inlier_rmse)
        self.fitnesses.append(reg.fitness)
        self.distances.append(np.sqrt(np.dot(movement,movement)))

        print(f"    > Time usage: {self.timeUsages[-1]:0.4f} seconds.")

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