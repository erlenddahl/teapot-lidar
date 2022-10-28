from ouster import client, pcap
import open3d as o3d
from colormaps import colorize, normalize
from sbetParser import SbetParser
import numpy as np
import os
import json
from datetime import datetime

class PcapReader:

    def __init__(self, pcap_path, meta_data_path = None, skip_frames = 0, sbet_path = None):
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
        
        self.max_distance = None

        self.internal_meta_path = pcap_path.replace(".pcap", ".pcap.meta.json")
        self.internal_meta = {}
        if os.path.isfile(self.internal_meta_path):
            try:
                with open(self.internal_meta_path) as f:
                    self.internal_meta = json.load(f)
            except:
                self.internal_meta = {}

        self.frame_coordinates = None
        if sbet_path is not None:
            self.sbet = SbetParser(sbet_path)
            self.gps_week = self.sbet.get_gps_week(pcap_path = self.pcap_path)
        else:
            self.sbet = None

        self.reset()

    def count_frames(self, show_progress = False):
        if "frame_count" not in self.internal_meta:
            if show_progress:
                print("Counting frames ...")
            return len(list(self.enumerate_lidar_packets()))
        return self.internal_meta["frame_count"]

    def save_internal_meta(self):
        with open(self.internal_meta_path, 'w') as f:
            json.dump(self.internal_meta, f)

    def reset(self):
        self.source.reset()
        self.scans = iter(client.Scans(self.source))
        self.last_read_frame_ix = -1

    def skip_and_get(self, iterator):
        try:
            for _ in range(self.skip_frames):
                self.last_read_frame_ix += 1
                next(iterator)
            self.last_read_frame_ix += 1
            return next(iterator)
        except StopIteration:
            return None

    def print_info(self, frame_index = None, printFunc = print):
        """Print information about all the packets in this file."""

        source = pcap.Pcap(self.pcap_path, self.metadata)
        ix = -1
        imu = -1

        for packet in source:
            if isinstance(packet, client.LidarPacket):

                ix += 1

                if frame_index is not None and ix != frame_index:
                    continue
                
                frame_id = packet.header(client.ColHeader.FRAME_ID)

                encoder_counts = packet.header(client.ColHeader.ENCODER_COUNT)
                timestamps = packet.header(client.ColHeader.TIMESTAMP)
                measurement_id = packet.header(client.ColHeader.MEASUREMENT_ID)
                status = packet.header(client.ColHeader.STATUS)

                ranges = packet.field(client.ChanField.RANGE)
                reflectivity = packet.field(client.ChanField.REFLECTIVITY)
                signal = packet.field(client.ChanField.SIGNAL)
                near_ir = packet.field(client.ChanField.NEAR_IR)

                printFunc("")
                printFunc("Headers:")
                printFunc(f'  encoder counts = {encoder_counts}')
                printFunc(f'  timestamps = {timestamps}')
                printFunc(f'  frame_index = {ix}')
                printFunc(f'  frame_id = {frame_id}')
                printFunc(f'  measurement_id = {measurement_id}')
                printFunc(f'  status = {status}')

                printFunc("")
                printFunc("Channels:")
                printFunc(f'  ranges = {ranges.shape}')
                printFunc(f'  reflectivity = {reflectivity.shape}')
                printFunc(f'  signal = {signal.shape}')
                printFunc(f'  near_ir = {near_ir.shape}')

                if self.sbet is not None:
                    printFunc(self.sbet.get_position(self.get_sbet_timestamp(packet), gps_week=self.gps_week))

            elif isinstance(packet, client.ImuPacket):

                imu += 1

                if frame_index is not None and ix <= frame_index:
                    continue

                # and access ImuPacket content
                printFunc("")
                printFunc("IMU packet " + str(imu) + ": ")
                printFunc(f'  sys_ts = {packet.sys_ts}')
                printFunc(f'  acceleration_ts = {packet.accel_ts}')
                printFunc(f'  acceleration = {packet.accel}')
                printFunc(f'  gyro_ts = {packet.gyro_ts}')
                printFunc(f'  angular_velocity = {packet.angular_vel}')
                
                if frame_index is not None:
                    break

    def enumerate_lidar_packets(self):
        count = 0
        min_time = 9223372036854775807
        max_time = -9223372036854775807
        find_bounds = "min_time_unix" not in self.internal_meta
        find_count = "frame_count" not in self.internal_meta

        source = pcap.Pcap(self.pcap_path, self.metadata)
        last_frame_id = -1
        for packet in source:
            if isinstance(packet, client.LidarPacket):
                frame_id = packet.header(client.ColHeader.FRAME_ID)[0]
                
                if find_bounds:
                    timestamps = packet.header(client.ColHeader.TIMESTAMP)
                    min_time = min(min_time, timestamps[0])
                    max_time = max(max_time, timestamps[1])

                if frame_id != last_frame_id:
                    count += 1
                    last_frame_id = frame_id

                    yield packet

        self.internal_meta["frame_count"] = count
        if find_bounds:

            self.internal_meta["min_time_unix"] = int(min_time)
            self.internal_meta["max_time_unix"] = int(max_time)
            
            self.internal_meta["min_time_human"] = datetime.utcfromtimestamp(min_time/1000000000).strftime("%Y-%m-%d %H:%M:%S")
            self.internal_meta["max_time_human"] = datetime.utcfromtimestamp(max_time/1000000000).strftime("%Y-%m-%d %H:%M:%S")

            print(self.internal_meta)

        if find_bounds or find_count:
            self.save_internal_meta()

    def get_coordinates(self):
        """Returns a list of coordinates (SbetRow) corresponding to each LidarPacket in the current Pcap file."""

        if self.sbet is None:
            return None

        positions = []
        self.sbet.reset()
        for packet in self.enumerate_lidar_packets():
            pos = self.sbet.get_position(self.get_sbet_timestamp(packet), gps_week=self.gps_week, continue_from_previous=True)
            positions.append(pos)

        return SbetParser.rotate_points(positions, positions[0].heading - np.pi / 2)

    def get_current_frame_index(self):
        return self.last_read_frame_ix

    def get_current_position(self):
        if self.sbet is None:
            return None
        if self.frame_coordinates is None:
            self.frame_coordinates = self.get_coordinates()
        return self.frame_coordinates[max(0, self.last_read_frame_ix)]

    def get_sbet_timestamp(self, packet = None, timestamps = None):
        if timestamps is None:
            timestamps = packet.header(client.ColHeader.TIMESTAMP)

        # There is a very slight difference, but using the final timestamp seems to give the best position.
        return timestamps[-1]

    def remove_vehicle(self, frame, cloud = None):
        # Remove the vehicle, which is always stationary at the center. We don't want that
        # to interfere with the point cloud alignment.

        if cloud is None:
            cloud = frame

        vw = 0.7
        vl = 2.2
        return cloud[((frame[:, 0] > 0.2) | (frame[:, 0] < -vl)) | ((frame[:, 1] > vw) | (frame[:, 1] < -vw)) | ((frame[:, 2] > 0.3) | (frame[:, 2] < -2))]

    def remove_invalid(self, frame, cloud = None):
        # Remove the vehicle, which is always stationary at the center. We don't want that
        # to interfere with the point cloud alignment.

        if cloud is None:
            cloud = frame

        return cloud[(frame[:, 0] != 0) & (frame[:, 1] != 0) & (frame[:, 2] != 0)]

    def remove_outside_distance(self, meters, frame, cloud = None):
        # Remove the vehicle, which is always stationary at the center. We don't want that
        # to interfere with the point cloud alignment.

        if cloud is None:
            cloud = frame

        return cloud[np.sqrt(frame[:,0]**2+frame[:,1]**2+frame[:,2]**2) <= meters]

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
        else:
            color_img = self.remove_invalid(xyz, color_img)
            xyz = self.remove_invalid(xyz)
            if timer is not None: timer.time("frame invalid values removal")

        if self.max_distance is not None:
            color_img = self.remove_outside_distance(self.max_distance, xyz, color_img)
            xyz = self.remove_outside_distance(self.max_distance, xyz)
            if timer is not None: timer.time("frame max distance removal")

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

if __name__ == "__main__":

    import argparse
    from pcapReaderHelper import PcapReaderHelper

    parser = argparse.ArgumentParser()
    PcapReaderHelper.add_path_arguments(parser)
    parser.add_argument('--output', type=str, required=True, help="A text file where all packet info should be saved.")

    args = parser.parse_args()

    reader = PcapReaderHelper.from_path_args(args)

    with open(args.output, 'w') as f:
        reader.print_info(printFunc=lambda l: f.write(l + "\n"))