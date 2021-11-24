from ouster import client, pcap
import open3d as o3d
from colormaps import colorize, normalize
import argparse

from pcapReader import PcapReader

class BufferedPcapReader(PcapReader):

    def __init__(self, pcapPath, metaDataPath = None, skip_frames = 0):
        """Initialize a LidarVisualizer by reading metadata and setting
        up a package source from the pcap file.
        """

        PcapReader.__init__(self, pcapPath, metaDataPath, skip_frames)

        self.preparedClouds = []

    def readFrame(self, num:int, removeVehicle:bool = False):
        """Retrieves the current frame from an array of read frames. The array is lazily
        filled with data from the pcap file as new frames are requested. Old frames are
        never thrown out, so this will case memory issues if the pcap file gets large enough."""

        # If given a negative index, return None.
        if num < 0:
            return None

        # Lazily read frames until the given index is available.
        while len(self.preparedClouds) < num + 1:
            self.preparedClouds.append(self.nextFrame())

        # Retrieve the requested frame, which will now be read.
        return self.preparedClouds[num]