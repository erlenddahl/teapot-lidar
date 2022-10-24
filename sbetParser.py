from sbetHelpers import read_sbet, filename2gpsweek, timestamp_unix2sow
import os
import numpy as np

class SbetRow:

    def __init__(self, sow, row):
        self.sow = row["time"]
        self.lat = row["lat"]
        self.lon = row["lon"]
        self.age = sow - row["time"]

    def __str__(self):
        return f'  lat={self.lat}, lon={self.lon}, time={self.sow}, age={self.age}'

class SbetParser:

    def __init__(self, sbet_filename):
        self.rows = SbetParser.read_latlon(sbet_filename, sbet_filename.replace(".out", "-smrmsg.out"))
        self.current_index = 0

    def get_position(self, timestamp = None, pcap_filename = None, pcap_path = None, gps_week = None):

        if gps_week is None:
            gps_week = self.get_gps_week(pcap_path, pcap_filename)
        
        # Calculate "Seconds of week", which is the time format used in the sbet files
        sow = timestamp_unix2sow(timestamp / 1000000000, gps_week)

        for i in range(len(self.rows)):
            if i == 0: continue
            if self.rows[i]["time"] >= sow:
                return SbetRow(sow, self.rows[i-1])
        
        return None

    def get_gps_week(self, pcap_path = None, pcap_filename = None):
        if pcap_path is not None:
            pcap_filename = os.path.basename(pcap_path)
        return filename2gpsweek(pcap_filename)

    @staticmethod
    def read_latlon(sbet_filename, smrmsg_filename):

        (sbet, _) = read_sbet(sbet_filename, smrmsg_filename)
        sbet = sbet[["time", "lat", "lon"]]
        sbet["lat"] = sbet["lat"] * 180 / np.pi
        sbet["lon"] = sbet["lon"] * 180 / np.pi
        
        return sbet