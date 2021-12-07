from bufferedPcapReader import BufferedPcapReader
from pcapReaderHelper import PcapReaderHelper
from open3dVisualizer import Open3DVisualizer
import open3d as o3d
import numpy as np

class PcapBrowser:

    def __init__(self, pcap_path, metadata_path):
        """Initialize a PcapBrowser by reading metadata and setting
        up a package source from the pcap file.
        """

        self.reader = BufferedPcapReader(pcap_path, metadata_path)
        self.vis = Open3DVisualizer()

        browser = self
        class RemoveVehicleProcessor:

            def process(self, cloud):
                xyz = np.asarray(cloud.points)
                colors = np.asarray(cloud.colors)
                
                colors = browser.reader.remove_vehicle(xyz, colors)
                xyz = browser.reader.remove_vehicle(xyz)

                cloud = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(xyz))
                cloud.colors = o3d.utility.Vector3dVector(colors)

                return cloud

        self.cloud_processors = [None, RemoveVehicleProcessor()]
        self.cloud_processor_index = 0
    
    def start_visualization(self):
        """Initializes an open3d visualizer, configures it to use arrow
        navigation, and open it displaying the first frame of lidar data
        from the pcap file."""
    
        self._currentFrame = 0

        # Use arrows to navigate to the next/previous frame
        def key_next(vis):
            self._currentFrame += 1
            if not self.set_frame(self._currentFrame):
                self._currentFrame -= 1

        def key_prev(vis):
            self._currentFrame -= 1
            if not self.set_frame(self._currentFrame):
                self._currentFrame += 1

        def key_toggle_thinning(vis):
            self.cloud_processor_index = (self.cloud_processor_index + 1) % len(self.cloud_processors)
            self.set_frame(self._currentFrame)

        self.vis.register_key_callback(262, key_next) # Arrow right
        self.vis.register_key_callback(263, key_prev) # Arrow left
        self.vis.register_key_callback(80, key_toggle_thinning) # P
        # List of key codes can be found here: https://www.glfw.org/docs/latest/group__keys.html

        self.set_frame(0)

        self.vis.reset_view()
        self.vis.run()

    def set_frame(self, num:int):
        """Show the frame with the given index in the visualizer. This function
        removes the geometry object containing the previous frame, then adds
        the geometry object containing the current frame. If the current frame is
        empty (end of file), this function does nothing, and returns False."""

        frame = self.read_frame(num)

        if frame is None:
            return False
        
        self.vis.show_frame(frame, True)

        self._currentFrame = num

        print("Showing frame ", num)

        return True

    def read_frame(self, num:int):
        """Retrieves the current frame from the reader object, processes it (if activated), and converts it to an open3d geometry."""

        frame = self.reader.read_frame(num)

        # If a cloud processor is active, process the cloud (for example by voxel thinning)
        if self.cloud_processors[self.cloud_processor_index] is not None:
            frame = self.cloud_processors[self.cloud_processor_index].process(frame)

        return frame
        

if __name__ == "__main__":

    args = PcapReaderHelper.get_path_args()

    # Create and start a visualization
    visualizer = PcapBrowser(args.pcap[0], args.json[0] if args.json is not None else None)
    visualizer.start_visualization()