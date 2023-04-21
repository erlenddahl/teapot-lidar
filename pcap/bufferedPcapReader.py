from ouster import client, pcap
import open3d as o3d
import argparse

from pcap.colormaps import colorize, normalize
from pcap.pcapReader import PcapReader

class BufferedPcapReader(PcapReader):

    def __init__(self, pcap_path, metadata_path, args):
        """Initialize a LidarVisualizer by reading metadata and setting
        up a package source from the pcap file.
        """

        PcapReader.__init__(self, pcap_path, metadata_path, 0, args)

        self.prepared_clouds = []

    def read_frame(self, num:int, remove_vehicle:bool = False):
        """Retrieves the current frame from an array of read frames. The array is lazily
        filled with data from the pcap file as new frames are requested. Old frames are
        never thrown out, so this will case memory issues if the pcap file gets large enough."""

        # If given a negative index, return None.
        if num < 0:
            return None

        # Lazily read frames until the given index is available.
        while len(self.prepared_clouds) < num + 1:
            self.prepared_clouds.append(self.next_frame(remove_vehicle))

        # Retrieve the requested frame, which will now be read.
        return self.prepared_clouds[num]

    def invalidate_cache(self):
        self.prepared_clouds = []
        self.reset()