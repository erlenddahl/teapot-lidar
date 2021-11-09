import pptk
from ouster import client, pcap
from contextlib import closing
from more_itertools import nth
import open3d as o3d
import numpy as np

class LidarVisualizer:

    def __init__(self, pcapPath, metaDataPath):

        self.pcapPath = pcapPath
        self.metaDataPath = metaDataPath

        # Read the metadata from the JSON file.
        with open(metaDataPath, "r") as f:
            self.metadata = client.SensorInfo(f.read())
        self.xyzLut = client.XYZLut(self.metadata)            

        self.source = pcap.Pcap(pcapPath, self.metadata)
        self.readFrames = []

    def printInfo(self):
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
        self.ctr.set_zoom(0.1)
        self.ctr.set_lookat([0, 0, 0])
        self.ctr.set_up([1, 0, 0])
    
    def startVisualization(self):
    
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

        def key_next(vis):
            self._currentFrame += 1
            if not self.setFrame(self._currentFrame):
                self._currentFrame -= 1

        def key_prev(vis):
            self._currentFrame -= 1
            if not self.setFrame(self._currentFrame):
                self._currentFrame += 1

        self.vis.register_key_callback(262, key_next) # Arrow right
        self.vis.register_key_callback(263, key_prev) # Arrow left
        # List of key codes can be found here: https://www.glfw.org/docs/latest/group__keys.html

        self.setFrame(0)
        self.reset_view()

        # run visualizer main loop
        print("Press Q or Excape to exit")

        self.vis.run()
        self.vis.destroy_window()

    def setFrame(self, num:int):

        newGeometry = self.readFrameGeometry(num)
        if newGeometry is None:
            return False
        
        if self._currentGeometry is not None:
            self.vis.remove_geometry(self._currentGeometry, False)

        self.vis.add_geometry(newGeometry, num == 0)

        self._currentGeometry = newGeometry
        self._currentFrame = num

        print("Showing frame ", num)

        return True

    def readFrameGeometry(self, num:int):

        if num < 0:
            return None

        while len(self.readFrames) < num + 1:
            scan = nth(client.Scans(self.source), 1)

            if scan is None:
                self.readFrames.append(None)
            else:
                xyz = self.xyzLut(scan)
                self.readFrames.append(o3d.geometry.PointCloud(o3d.utility.Vector3dVector(xyz.reshape((-1, 3)))))

        return self.readFrames[num]
        

if __name__ == "__main__":
    # Configure PCAP and JSON file paths
    pathBase = "data\\2021-10-05 - Honefoss med parkeringshus\\OS-1-128_992035000186_1024x10_20211005_134603"
    pcapPath = pathBase + ".pcap"
    metaDataPath = pathBase + ".json"

    visualizer = LidarVisualizer(pcapPath, metaDataPath)
    visualizer.startVisualization()