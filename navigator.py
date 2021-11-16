from voxelThinnerPyoints import VoxelThinnerPyoints
from pcapReader import PcapReader
from open3dVisualizer import Open3DVisualizer
import numpy as np

class LidarNavigator:

    def __init__(self, pcapPath, metaDataPath):
        """Initialize a LidarNavigator by reading metadata and setting
        up a package source from the pcap file.
        """

        self.reader = PcapReader(pcapPath, metaDataPath)

        # Fetch the first frame and use it as a base for the generated visualization
        self.ball_radius = 0.5
        self.thinner = VoxelThinnerPyoints()
        self.mergedFrame = self.thinner.process(self.reader.readFrame(0), self.ball_radius)

        self.vis = Open3DVisualizer()
        self.vis.showFrame(self.mergedFrame)

    def navigateThroughFile(self):

        self.vis.reset_view()

        while self.mergeNextFrame():
            self.vis.refresh_non_blocking()

    def mergeNextFrame(self):

        frame = self.reader.nextFrame()

        if frame is None:
            return False

        frame = self.thinner.process(frame, self.ball_radius)

        merged = np.concatenate((self.mergedFrame, frame))
        merged = self.thinner.process(merged, self.ball_radius)

        self.mergedFrame = merged

        self.vis.showFrame(self.mergedFrame, True)

        return True
        

if __name__ == "__main__":

    args = PcapReader.getPathArgs()

    # Create and start a visualization
    navigator = LidarNavigator(args.pcap, args.json)
    navigator.navigateThroughFile()