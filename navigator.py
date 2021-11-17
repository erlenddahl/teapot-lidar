from pcapReader import PcapReader
from open3dVisualizer import Open3DVisualizer
import numpy as np
import time
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
        
        self.vis = Open3DVisualizer()
        self.vis.refresh_non_blocking()

        self.movements = []
        self.mergedFrame = self.reader.readFrameAsPointCloud(0, True)
        self.previousFrame = self.reader.readFrameAsPointCloud(0, True)
        self.previousFrame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        self.vis.showFrame(self.mergedFrame)
        self.vis.reset_view()

        while self.mergeNextFrame():
            self.vis.refresh_non_blocking()

        self.vis.run()

    def alignFrame(self, source, target):
        threshold = 1
        trans_init = np.identity(4)

        startTime = time.perf_counter()
        print("Estimating normals")
        target.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        print("Performing point-to-plane registration")
        reg_p2l = o3d.pipelines.registration.registration_icp(
            source, target, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))
        print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

        movement = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(reg_p2l.transformation).get_center()

        return reg_p2l.transformation, movement

    def mergeNextFrame(self):

        frame = self.reader.nextFrameAsPointCloud(True)

        if frame is None:
            return False

        transformation, movement = self.alignFrame(self.previousFrame, frame)

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
        merged = self.mergedFrame.transform(transformation)
        merged += frame
        merged = merged.voxel_down_sample(voxel_size=self.voxel_size)
        print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

        self.mergedFrame = merged
        self.previousFrame = frame

        self.vis.showFrame(self.mergedFrame, True)

        return True
        

if __name__ == "__main__":

    args = PcapReader.getPathArgs()

    # Create and start a visualization
    navigator = LidarNavigator(args.pcap, args.json)
    navigator.navigateThroughFile()