from bufferedPcapReader import BufferedPcapReader
from open3dVisualizer import Open3DVisualizer

class PcapBrowser:

    def __init__(self, pcapPath, metaDataPath):
        """Initialize a PcapBrowser by reading metadata and setting
        up a package source from the pcap file.
        """

        self.reader = BufferedPcapReader(pcapPath, metaDataPath)
        self.vis = Open3DVisualizer()
    
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

        self.vis.register_key_callback(262, key_next) # Arrow right
        self.vis.register_key_callback(263, key_prev) # Arrow left
        # List of key codes can be found here: https://www.glfw.org/docs/latest/group__keys.html

        self.set_frame(0)

        self.vis.reset_view()
        self.vis.run()

    def set_frame(self, num:int):
        """Show the frame with the given index in the visualizer. This function
        removes the geometry object containing the previous frame, then adds
        the geometry object containing the current frame. If the current frame is
        empty (end of file), this function does nothing, and returns False."""

        frame = self.reader.read_frame(num)
        if frame is None:
            return False
        
        self.vis.show_frame(frame, True)

        self._currentFrame = num

        print("Showing frame ", num)

        return True
        

if __name__ == "__main__":

    args = BufferedPcapReader.getPathArgs()

    # Create and start a visualization
    visualizer = PcapBrowser(args.pcap, args.json)
    visualizer.start_visualization()