from sbet.sbetHelpers import read_sbet, filename2gpsweek, timestamp_unix2sow, timestamp_sow2unix
import os
import numpy as np
import open3d as o3d

from sbet.sbetRow import SbetRow

class SbetParser:

    def __init__(self, filename, z_offset):
        self.z_offset = z_offset
        self.rows = SbetParser.read_latlon(filename, filename.replace(".out", "-smrmsg.out"))
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
                return SbetRow(self.rows[i-1], sow, i, z_offset=self.z_offset)

        self.current_index = 0
        return None

    def get_gps_week(self, pcap_path = None, pcap_filename = None):
        if pcap_path is not None:
            pcap_filename = os.path.basename(pcap_path)
        return filename2gpsweek(pcap_filename)

    @staticmethod
    def read_latlon(sbet_filename, smrmsg_filename):

        (sbet, _) = read_sbet(sbet_filename, smrmsg_filename)
        sbet = sbet[["time", "lat", "lon", "alt", "heading"]]
        sbet["lat"] = sbet["lat"] * 180 / np.pi
        sbet["lon"] = sbet["lon"] * 180 / np.pi
        
        return sbet

    def get_rows(self):
        return [SbetRow(row, z_offset=self.z_offset) for row in self.rows]
    
    def get_rotated_rows(self):
        """ Returns all coordinates rotated so that the initial heading points due north. """
        coords = self.get_rows()
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