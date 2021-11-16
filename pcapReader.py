from ouster import client, pcap
from more_itertools import nth

class PcapReader:

    def __init__(self, pcapPath, metaDataPath = None):
        """Initialize a LidarVisualizer by reading metadata and setting
        up a package source from the pcap file.
        """

        self.pcapPath = pcapPath

        if metaDataPath is None or metaDataPath == "":
            metaDataPath = pcapPath.replace(".pcap", ".json")

        self.metaDataPath = metaDataPath

        # Read the metadata from the JSON file.
        with open(metaDataPath, "r") as f:
            self.metadata = client.SensorInfo(f.read())
        self.xyzLut = client.XYZLut(self.metadata)            

        self.source = pcap.Pcap(pcapPath, self.metadata)
        self.readFrames = []

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

    def readFrame(self, num:int):
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
        return self.readFrames[num]