from sbet.sbetHelpers import read_sbet, filename2gpsweek, filename2utc, timestamp_unix2sow, timestamp_sow2unix
import os
import numpy as np
import open3d as o3d
import csv
import random
from pyproj import Transformer

from sbet.sbetRow import SbetRow

class SbetParser:

    def __init__(self, filename, random_noise, noise_from_frame_ix=0, crs_from=4258, crs_to=5972):

        if filename.lower().endswith(".csv"):
            self.rows = SbetParser.read_csv(filename)
        else:
            self.rows = SbetParser.read_latlon(filename, filename.replace(".out", "-smrmsg.out"))

        self.random_noise = random_noise
        self.add_noise = random_noise is not None and (random_noise[0] > 0 or random_noise[1] > 0 or random_noise[2] > 0)

        self.current_index = 0
        self.row_count = len(self.rows)

        # Used for transforming read coordinates to the correct reference frame upon request.
        # Must be initialized with self.create_transformer, which is automatically called in 
        # get_position, but not get_rows.
        self.gps_epoch = None
        self.transformer = None
        self.current_filename = None

        self.crs_from = crs_from
        self.crs_to = crs_to
        self.transformer = Transformer.from_crs(self.crs_from, self.crs_to)

    def reset(self):
        self.current_index = 0

    def create_transformer(self, pcap_filename):
        self.gps_epoch = self.get_gps_epoch(pcap_filename)
        self.current_filename = pcap_filename

    def get_position(self, timestamp=None, pcap_filename=None, pcap_path=None, gps_week=None, continue_from_previous=False):

        if pcap_path is not None:
            pcap_filename = os.path.basename(pcap_path)

        if pcap_filename != self.current_filename:
            self.create_transformer(pcap_filename)

        if gps_week is None:
            gps_week = self.get_gps_week(pcap_path, pcap_filename)
        
        # Calculate "Seconds of week", which is the time format used in the sbet files
        sow = timestamp_unix2sow(timestamp / 1000000000, gps_week)

        start_ix = self.current_index if continue_from_previous else 1
        for i in range(start_ix, self.row_count):

            if self.rows[i]["time"] >= sow:
                self.current_index = i
                sbetRow = SbetRow(self.rows[i-1], sow, i)
                sbetRow.calculate_transformed(self.transformer, self.gps_epoch)

                if self.add_noise:
                    sbetRow.x += random.uniform(-self.random_noise[0], self.random_noise[0])
                    sbetRow.y += random.uniform(-self.random_noise[1], self.random_noise[1])
                    sbetRow.alt += random.uniform(-self.random_noise[2], self.random_noise[2])

                return sbetRow

        self.current_index = 0
        return None

    def get_gps_epoch(self, pcap_filename):

        utc = filename2utc(pcap_filename)

        return self.get_gps_epoch_from_utc(utc)

    def get_gps_epoch_from_utc(self, utc):

        dayofyear = utc.timetuple().tm_yday
        currentepoch = utc.year + dayofyear / 365 # Current Epoch ex: 2021.45

        return currentepoch

    def get_gps_week(self, pcap_path = None, pcap_filename = None):
        if pcap_path is not None:
            pcap_filename = os.path.basename(pcap_path)
        return filename2gpsweek(pcap_filename)

    @staticmethod
    def read_csv(filename):
        # Can also read CSV files with the headers index,time,lat,lon,alt,heading (since some SBET files didn't work with this reader).
        rows = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row["index"] = int(row["index"])
                row["time"] = float(row["time"])
                row["lat"] = float(row["lat"])
                row["lon"] = float(row["lon"])
                row["alt"] = float(row["alt"])
                row["heading"] = float(row["heading"])
                rows.append(row)
        return rows


    @staticmethod
    def read_latlon(sbet_filename, smrmsg_filename):

        (sbet, mmr) = read_sbet(sbet_filename, smrmsg_filename)
        sbet = sbet[["time", "lat", "lon", "alt", "heading"]]
        sbet["lat"] = sbet["lat"] * 180 / np.pi
        sbet["lon"] = sbet["lon"] * 180 / np.pi
        
        return sbet

    def get_rows(self, rotate=False):
        coords = [SbetRow(row).calculate_transformed(self.transformer, self.gps_epoch) for row in self.rows]
        if not rotate:
            return coords
        return SbetParser.rotate_points(coords, coords[0].heading)

    @staticmethod
    def rotate_points(coords, heading):
        """ Returns all coordinates rotated by the given heading. """

        transformed_path = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector([[p.x, p.y, p.alt] for p in coords]), lines = o3d.utility.Vector2iVector([])
        )
        R = transformed_path.get_rotation_matrix_from_xyz((0, 0, heading))
        transformed_path.rotate(R, center=transformed_path.points[0])

        for i in range(len(coords)):
            c = coords[i]
            c.lat = -1
            c.lon = -1
            c.x = transformed_path.points[i][0]
            c.y = transformed_path.points[i][1]
        
        return coords