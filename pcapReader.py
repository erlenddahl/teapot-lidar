from ouster import client, pcap
import open3d as o3d
from colormaps import colorize, normalize

class PcapReader:

    def __init__(self, pcap_path, meta_data_path = None, skip_frames = 0):
        """Initialize a LidarVisualizer by reading metadata and setting
        up a package source from the pcap file.
        """

        self.pcap_path = pcap_path

        if meta_data_path is None or meta_data_path == "":
            meta_data_path = pcap_path.replace(".pcap", ".json")

        self.meta_data_path = meta_data_path

        # Read the metadata from the JSON file.
        with open(meta_data_path, "r") as f:
            self.metadata = client.SensorInfo(f.read())
        self.xyzLut = client.XYZLut(self.metadata)            

        self.source = pcap.Pcap(pcap_path, self.metadata)

        self.channels = [c for c in client.ChanField]

        # If 0, every frame will be read. If 1, every second frame, etc.
        self.skip_frames = skip_frames

        self.reset()

    def count_frames(self):
        count = 0
        i = iter(client.Scans(self.source))
        while True:
            frame = self.skip_and_get(i)
            if frame is None:
                break
            count += 1
        self.reset()
        return count

    def reset(self):
        self.source.reset()
        self.scans = iter(client.Scans(self.source))

    def skip_and_get(self, iterator):
        try:
            for _ in range(self.skip_frames):
                next(iterator)
            return next(iterator)
        except StopIteration:
            return None

    def print_info(self):
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

    def remove_vehicle(self, frame, cloud = None):
        # Remove the vehicle, which is always stationary at the center. We don't want that
        # to interfere with the point cloud alignment.

        if cloud is None:
            cloud = frame

        vr = 2.5
        return cloud[((frame[:, 0] > vr) | (frame[:, 0] < -vr)) | ((frame[:, 1] > vr) | (frame[:, 1] < -vr))]

    def next_frame(self, remove_vehicle:bool = False, timer = None):
        """Retrieves the next frame"""

        if timer is not None: timer.reset()

        scan = self.skip_and_get(self.scans)

        if timer is not None: timer.time("frame retrieval")

        if scan is None:
            return None
            
        # Prepare the frame for visualization
        xyz = self.xyzLut(scan)
        xyz = xyz.reshape((-1, 3))

        if timer is not None: timer.time("frame reshaping")

        key = scan.field(self.channels[1])

        # apply colormap to field values
        key_img = normalize(key)
        color_img = colorize(key_img)
        color_img = color_img.reshape((-1, 3))

        if timer is not None: timer.time("frame colorization")

        if remove_vehicle:
            color_img = self.remove_vehicle(xyz, color_img)
            xyz = self.remove_vehicle(xyz)
            if timer is not None: timer.time("frame vehicle removal")

        cloud = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(xyz))
        cloud.colors = o3d.utility.Vector3dVector(color_img)

        if timer is not None: timer.time("frame cloud generation")

        return cloud

    def read_all_frames(self, remove_vehicle:bool = False):

        frames = []
        while True:
            frame = self.next_frame(remove_vehicle)
            if frame is None:
                return frames
            frames.append(frame)