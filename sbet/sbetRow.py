import math
import numpy as np
from pyproj import Transformer

transformer = Transformer.from_crs(4326, 5972)
class SbetRow:
    """
    A data row from an SBET file. Contains the original coordinates as lat/lon, and transformed (to 5972) as x and y. The heading is in radians,
    0 means straight north, positive PI/2 means straight east, negative PI/2 straight west.
    """

    def __init__(self, row, sow=0, index=0, original=None, z_offset=0, x=None, y=None):

        if row is None and x is not None and y is not None:
            self.x = x
            self.y = y
            self.alt = 0
            self.sow = 0
            self.lat = 0
            self.lon = 0
            self.age = 0
            self.index = 0
            self.heading = 0
            return

        if original is not None:

            if type(original) is not dict:
                original = original.__dict__
                
            self.sow = original["sow"]
            self.lat = original["lat"]
            self.lon = original["lon"]
            self.alt = original["alt"]
            self.age = original["age"]
            self.index = original["index"]
            self.x = original["x"]
            self.y = original["y"]
            self.heading = original["heading"]
            return

        self.sow = row["time"]
        self.lat = row["lat"]
        self.lon = row["lon"]
        self.alt = row["alt"] + z_offset
        self.age = sow - row["time"]
        self.heading = row["heading"]
        self.index = index

        self.x, self.y = transformer.transform(self.lat, self.lon)

    def __str__(self, include_lat_lon=True):
        return f'ix={self.index}' + (f', lat={self.lat}, lon={self.lon}, heading={self.heading}' if include_lat_lon else '') + f', alt={self.alt}, x={self.x}, y={self.y}, time={self.sow}, age={self.age}'

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
            json["heading"] = self.heading
            json["index"] = self.index

        return json

    def get_csv_headers(self):
        return ["index", "time", "lat", "lon", "alt", "heading", "x", "y"]

    def get_csv(self):
        return [self.index, self.sow, self.lat, self.lon, self.alt, self.heading, self.x, self.y]

    def distance2d(self, p):
        dx = p.x - self.x
        dy = p.y - self.y
        return math.sqrt(dx*dx + dy*dy)

    def translate(self, t):
        self.x += t[0]
        self.y += t[1]
        self.alt += t[2]
        return self

    def np(self):
        return np.array([self.x, self.y, self.alt])