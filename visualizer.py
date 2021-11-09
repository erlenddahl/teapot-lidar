from ouster import client, pcap
from voxelThinner import VoxelThinner
from more_itertools import nth
import open3d as o3d
import numpy as np

class LidarVisualizer:

    def __init__(self, pcapPath, metaDataPath):
        """Initialize a LidarVisualizer by reading metadata and setting
        up a package source from the pcap file.
        """

        self.pcapPath = pcapPath
        self.metaDataPath = metaDataPath

        # Read the metadata from the JSON file.
        with open(metaDataPath, "r") as f:
            self.metadata = client.SensorInfo(f.read())
        self.xyzLut = client.XYZLut(self.metadata)            

        self.source = pcap.Pcap(pcapPath, self.metadata)
        self.readFrames = []
        self.cloudProcessor = None
        self._isInitialGeometry = True

    def printInfo(self):
        """Print information about all the packets in this file."""

        for packet in self.source:
            if isinstance(packet, client.LidarPacket):
                # Now we can process the LidarPacket. In this case, we access
                # the encoder_counts, timestamps, and ranges
                encoder_counts = packet.header(client.ColHeader.ENCODER_COUNT)
                timestamps = packet.header(client.ColHeader.TIMESTAMP)
                ranges = packet.field(client.ChanField.RANGE)
                print(f'  encoder counts = {encoder_counts.shape}')
                print(f'  timestamps = {timestamps.shape}')
                print(f'  ranges = {ranges.shape}')

            elif isinstance(packet, client.ImuPacket):
                # and access ImuPacket content
                print(f'  acceleration = {packet.accel}')
                print(f'  angular_velocity = {packet.angular_vel}')

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
            if self.cloudProcessor is None:
                self.cloudProcessor = VoxelThinner()
            else:
                self.cloudProcessor = None

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
        """Retrieves the current frame from an array of read frames. The array is lazily
        filled with data from the pcap file as new frames are requested. Old frames are
        never thrown out, so this will case memory issues if the pcap file gets large enough."""

        # If given a negative index, return None.
        if num < 0:
            return None

        # Lazily read frames until the given index is available.
        while len(self.readFrames) < num + 1:
            scan = nth(client.Scans(self.source), 1)

            if scan is None:
                self.readFrames.append(None)
            else:
                # Prepare the frame for visualization
                xyz = self.xyzLut(scan)
                xyz = xyz.reshape((-1, 3))

                self.readFrames.append(xyz)

        # Retrieve the requested frame, which will now be read.
        frame = self.readFrames[num]

        # If a cloud processor is active, process the cloud (for example by voxel thinning)
        if self.cloudProcessor is not None:
            frame = self.cloudProcessor.process(frame)

        # Return it as an open3d geometry
        return o3d.geometry.PointCloud(o3d.utility.Vector3dVector(frame))
        

if __name__ == "__main__":
    # Configure PCAP and JSON file paths
    pathBase = "data\\2021-10-05 - Honefoss med parkeringshus\\OS-1-128_992035000186_1024x10_20211005_134603"
    pcapPath = pathBase + ".pcap"
    metaDataPath = pathBase + ".json"

    # Create and start a visualization
    visualizer = LidarVisualizer(pcapPath, metaDataPath)
    visualizer.startVisualization()