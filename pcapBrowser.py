from bufferedPcapReader import BufferedPcapReader
from pcapReaderHelper import PcapReaderHelper
from open3dVisualizer import Open3DVisualizer
import argparse
import open3d as o3d
import numpy as np
import os

class PcapBrowser:

    def __init__(self, pcap_path, metadata_path, save_screenshots_to):
        """Initialize a PcapBrowser by reading metadata and setting
        up a package source from the pcap file.
        """

        self.reader = BufferedPcapReader(pcap_path, metadata_path)
        self.vis = Open3DVisualizer()
        self.save_screenshots_to = save_screenshots_to

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

        def key_print_info(vis):
            self.reader.print_info(self._currentFrame)

        def key_increase_max_distance(vis):
            if self.reader.max_distance is None:
                self.reader.max_distance = 0
            self.reader.max_distance += 1
            print("Max distance:", self.reader.max_distance)
            
            self.reader.invalidate_cache()
            self.set_frame(self._currentFrame)

        def key_decrease_max_distance(vis):
            if self.reader.max_distance is None:
                return
            
            self.reader.max_distance -= 1
            if self.reader.max_distance < 1:
                self.reader.max_distance = None

            print("Max distance:", self.reader.max_distance)
            
            self.reader.invalidate_cache()
            self.set_frame(self._currentFrame)

        self.vis.register_key_callback(262, key_next) # Arrow right
        self.vis.register_key_callback(263, key_prev) # Arrow left
        self.vis.register_key_callback(73, key_print_info) # I
        self.vis.register_key_callback(80, key_toggle_thinning) # P
        self.vis.register_key_callback(75, key_decrease_max_distance) # K
        self.vis.register_key_callback(76, key_increase_max_distance) # L
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

        if self.save_screenshots_to is not None:
            screenshot_path = os.path.join(self.save_screenshots_to, str(num) + ".png")
            self.vis.capture_screen_image(screenshot_path)
            print("Saved screenshot")

        return True

    def read_frame(self, num:int):
        """Retrieves the current frame from the reader object, processes it (if activated), and converts it to an open3d geometry."""

        frame = self.reader.read_frame(num)

        # If a cloud processor is active, process the cloud (for example by voxel thinning)
        if self.cloud_processors[self.cloud_processor_index] is not None:
            frame = self.cloud_processors[self.cloud_processor_index].process(frame)

        return frame
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    PcapReaderHelper.add_path_arguments(parser)
    parser.add_argument('--save-screenshots-to', type=str, default=None, required=False, help="If given, point cloud screenshots will be saved in this directory with their indices as filenames (0.png, 1.png, 2.png, etc). Only works if --preview is set to 'always'.")
    args = parser.parse_args()

    # Create and start a visualization
    visualizer = PcapBrowser(args.pcap[0], args.json[0] if args.json is not None else None, args.save_screenshots_to)
    visualizer.start_visualization()