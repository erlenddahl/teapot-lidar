from sbetHelpers import read_sbet, filename2gpsweek, timestamp_unix2sow, timestamp_sow2unix
import os
import numpy as np
from pyproj import Transformer
from datetime import datetime

transformer = Transformer.from_crs(4326, 5972)
class SbetRow:

    def __init__(self, sow, row, index, original = None):

        if original is not None:
            self.sow = original.sow
            self.lat = original.lat
            self.lon = original.lon
            self.alt = original.alt
            self.age = original.age
            self.index = original.index
            self.x = original.x
            self.y = original.y
            return

        self.sow = row["time"]
        self.lat = row["lat"]
        self.lon = row["lon"]
        self.alt = row["alt"]
        self.age = sow - row["time"]
        self.index = index

        self.x, self.y = transformer.transform(self.lat, self.lon)

    def __str__(self):
        return f'ix={self.index}, lat={self.lat}, lon={self.lon}, alt={self.alt}, x={self.x}, y={self.y}, time={self.sow}, age={self.age}'

    def clone(self):
        return SbetRow(None, None, None, self)

    def json(self, actual = False):
        json = {
            "x": self.x,
            "y": self.y,
            "z": self.alt
        }

        if actual:
            json["age"] = self.age

        return json

class SbetParser:

    def __init__(self, sbet_filename):
        self.rows = SbetParser.read_latlon(sbet_filename, sbet_filename.replace(".out", "-smrmsg.out"))
        self.current_index = 0
        self.row_count = len(self.rows)

    def reset(self):
        self.current_index = 0

    def get_position(self, timestamp = None, pcap_filename = None, pcap_path = None, gps_week = None, continue_from_previous = False):

        if gps_week is None:
            gps_week = self.get_gps_week(pcap_path, pcap_filename)
        
        # Calculate "Seconds of week", which is the time format used in the sbet files
        sow = timestamp_unix2sow(timestamp / 1000000000, gps_week)

        start_ix = self.current_index if continue_from_previous else 1
        for i in range(start_ix, self.row_count):

            if self.rows[i]["time"] >= sow:
                self.current_index = i
                return SbetRow(sow, self.rows[i-1], i)

        self.current_index = 0
        return None

    def get_gps_week(self, pcap_path = None, pcap_filename = None):
        if pcap_path is not None:
            pcap_filename = os.path.basename(pcap_path)
        return filename2gpsweek(pcap_filename)

    @staticmethod
    def read_latlon(sbet_filename, smrmsg_filename):

        (sbet, _) = read_sbet(sbet_filename, smrmsg_filename)
        sbet = sbet[["time", "lat", "lon", "alt"]]
        sbet["lat"] = sbet["lat"] * 180 / np.pi
        sbet["lon"] = sbet["lon"] * 180 / np.pi
        
        return sbet

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sbet', type=str, required=True, help="The path to a corresponding SBET file with GNSS coordinates.")
    parser.add_argument('--gps-week', type=int, default=-1, required=False, help="If given, this GPS week will be used to transform the timestamps to unix and human readable time.")
    args = parser.parse_args()

    # Create and start a visualization
    parser = SbetParser(args.sbet)
    
    min_time = np.min(parser.rows["time"])
    max_time = np.max(parser.rows["time"])

    print("Min time:", min_time)
    print("Max time:", max_time)

    if args.gps_week >= 0:

        print("With GPS week:", args.gps_week)
        
        min_unix_time = timestamp_sow2unix(min_time, args.gps_week)
        max_unix_time = timestamp_sow2unix(max_time, args.gps_week)
        print("Min unix time:", min_unix_time)
        print("Max unix time:", max_unix_time)
        
        print("Min human time:", datetime.utcfromtimestamp(min_unix_time).strftime("%Y-%m-%d %H:%M:%S"))
        print("Max human time:", datetime.utcfromtimestamp(max_unix_time).strftime("%Y-%m-%d %H:%M:%S"))

    print("Min lat:", np.min(parser.rows["lat"]))
    print("Max lat:", np.max(parser.rows["lat"]))
    
    print("Min lon:", np.min(parser.rows["lon"]))
    print("Max lon:", np.max(parser.rows["lon"]))