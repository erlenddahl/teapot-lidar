from ouster import client, pcap
from more_itertools import nth
import open3d

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

    def removeVehicle(self, frame):
        # Remove the vehicle, which is always stationary at the center. We don't want that
        # to interfere with the point cloud alignment.
        vr = 2.5
        return frame[((frame[:, 0] > vr) | (frame[:, 0] < -vr)) | ((frame[:, 1] > vr) | (frame[:, 1] < -vr))]

    def readFrame(self, num:int, removeVehicle:bool = False):
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

                if removeVehicle:
                    xyz = self.removeVehicle(xyz)

                self.readFrames.append(xyz)

        # Retrieve the requested frame, which will now be read.
        return self.readFrames[num]

    def readFrameAsPointCloud(self, num:int, removeVehicle:bool = False):
        
        frame = self.readFrame(num, removeVehicle)

        return open3d.geometry.PointCloud(open3d.utility.Vector3dVector(frame))

    def nextFrame(self, removeVehicle:bool = False):
        """Reads and returns the first unread frame"""

        return self.readFrame(len(self.readFrames), removeVehicle)

    def nextFrameAsPointCloud(self, removeVehicle:bool = False):
        return open3d.geometry.PointCloud(open3d.utility.Vector3dVector(self.nextFrame(removeVehicle)))

    @staticmethod
    def getPathArgs():
        """ Creates an argument parser that handles --pcap and --json, where the latter is optional.
        If --json is not given, it will be replaced with the values of the --pcap parameter with the file
        extension changed to .json.
        """
        
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('--pcap', type=str, required=True, help="The path to the PCAP file to visualize, relative or absolute.")
        parser.add_argument('--json', type=str, required=False, help="The path to the corresponding JSON file with the sensor metadata, relative or absolute. If this is not given, the PCAP location is used (by replacing .pcap with .json).")
        args = parser.parse_args()

        if args.json is None:
            args.json = args.pcap.replace(".pcap", ".json")

        return args

    @staticmethod
    def fromPathArgs():
        args = PcapReader.getPathArgs()
        return PcapReader(args.pcap, args.json)