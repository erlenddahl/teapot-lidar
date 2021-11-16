from voxelThinner import VoxelThinner
from voxelThinnerPyoints import VoxelThinnerPyoints
import open3d as o3d
import numpy as np
import argparse
from pcapReader import PcapReader

class LidarVisualizer:

    def __init__(self, pcapPath, metaDataPath):
        """Initialize a LidarVisualizer by reading metadata and setting
        up a package source from the pcap file.
        """

        self.reader = PcapReader(pcapPath, metaDataPath)

        self.cloudProcessors = [None, VoxelThinner(), VoxelThinnerPyoints()]
        self.cloudProcessorIndex = 0
        self._isInitialGeometry = True

    def reset_view(self):
        """Reset the view to the axis center"""
        self.ctr.set_zoom(0.1)
        self.ctr.set_lookat([0, 0, 0])
        self.ctr.set_up([1, 0, 0])
    
    def startVisualization(self):
        """Initializes an open3d visualizer, configures it to use arrow
        navigation, and open it displaying the first frame of lidar data
        from the pcap file."""
    
        # Create a simple axis visualization
        axes = o3d.geometry.TriangleMesh.create_coordinate_frame(1.0)

        # initialize visualizer and rendering options
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window()
        self.vis.add_geometry(axes)

        ropt = self.vis.get_render_option()
        ropt.point_size = 1.0
        ropt.background_color = np.asarray([0, 0, 0])

        # initialize camera settings
        self.ctr = self.vis.get_view_control()

        self._currentFrame = 0
        self._currentGeometry = None

        # Use arrows to navigate to the next/previous frame
        def key_next(vis):
            self._currentFrame += 1
            if not self.setFrame(self._currentFrame):
                self._currentFrame -= 1

        def key_prev(vis):
            self._currentFrame -= 1
            if not self.setFrame(self._currentFrame):
                self._currentFrame += 1

        def key_toggle_thinning(vis):
            self.cloudProcessorIndex = (self.cloudProcessorIndex + 1) % len(self.cloudProcessors)
            self.setFrame(self._currentFrame)

        self.vis.register_key_callback(262, key_next) # Arrow right
        self.vis.register_key_callback(263, key_prev) # Arrow left
        self.vis.register_key_callback(80, key_toggle_thinning) # P
        # List of key codes can be found here: https://www.glfw.org/docs/latest/group__keys.html

        self.setFrame(0)
        self.reset_view()

        # run visualizer main loop
        print("Press Q or Excape to exit")

        self.vis.run()
        self.vis.destroy_window()

    def setFrame(self, num:int):
        """Show the frame with the given index in the visualizer. This function
        removes the geometry object containing the previous frame, then adds
        the geometry object containing the current frame. If the current frame is
        empty (end of file), this function does nothing, and returns False."""

        newGeometry = self.readFrameGeometry(num)
        if newGeometry is None:
            return False
        
        if self._currentGeometry is not None:
            self.vis.remove_geometry(self._currentGeometry, False)

        self.vis.add_geometry(newGeometry, self._isInitialGeometry)
        self._isInitialGeometry = False

        self._currentGeometry = newGeometry
        self._currentFrame = num

        print("Showing frame ", num)

        return True

    def readFrameGeometry(self, num:int):
        """Retrieves the current frame from the reader object, processes it (if activated), and converts it to an open3d geometry."""

        frame = self.reader.readFrame(num)

        # If a cloud processor is active, process the cloud (for example by voxel thinning)
        if self.cloudProcessors[self.cloudProcessorIndex] is not None:
            frame = self.cloudProcessors[self.cloudProcessorIndex].process(frame)

        # Return it as an open3d geometry
        return o3d.geometry.PointCloud(o3d.utility.Vector3dVector(frame))
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap', type=str, required=True, help="The path to the PCAP file to visualize, relative or absolute.")
    parser.add_argument('--json', type=str, required=False, help="The path to the corresponding JSON file with the sensor metadata, relative or absolute. If this is not given, the PCAP location is used (by replacing .pcap with .json).")
    args = parser.parse_args()

    if args.json is None:
        args.json = args.pcap.replace(".pcap", ".json")

    # Create and start a visualization
    visualizer = LidarVisualizer(args.pcap, args.json)
    visualizer.startVisualization()