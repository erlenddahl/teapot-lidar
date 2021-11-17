from pcapReader import PcapReader
from open3dVisualizer import Open3DVisualizer

class PcapBrowser:

    def __init__(self, pcapPath, metaDataPath):
        """Initialize a PcapBrowser by reading metadata and setting
        up a package source from the pcap file.
        """

        self.reader = PcapReader(pcapPath, metaDataPath)
        self.vis = Open3DVisualizer()

        self.cloudProcessors = [None]
        self.cloudProcessorIndex = 0
    
    def startVisualization(self):
        """Initializes an open3d visualizer, configures it to use arrow
        navigation, and open it displaying the first frame of lidar data
        from the pcap file."""
    
        self._currentFrame = 0

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

        self.vis.run()

    def setFrame(self, num:int):
        """Show the frame with the given index in the visualizer. This function
        removes the geometry object containing the previous frame, then adds
        the geometry object containing the current frame. If the current frame is
        empty (end of file), this function does nothing, and returns False."""

        frame = self.readFrame(num)
        if frame is None:
            return False
        
        self.vis.showFrame(frame, True)

        self._currentFrame = num

        print("Showing frame ", num)

        return True

    def readFrame(self, num:int):
        """Retrieves the current frame from the reader object, processes it (if activated), and converts it to an open3d geometry."""

        frame = self.reader.readFrame(num)

        # If a cloud processor is active, process the cloud (for example by voxel thinning)
        if self.cloudProcessors[self.cloudProcessorIndex] is not None:
            frame = self.cloudProcessors[self.cloudProcessorIndex].process(frame)

        return frame
        

if __name__ == "__main__":

    args = PcapReader.getPathArgs()

    # Create and start a visualization
    visualizer = PcapBrowser(args.pcap, args.json)
    visualizer.startVisualization()