from pyoints import filters
from pyoints.indexkd import IndexKD

class VoxelThinnerPyoints:

    def __init__(self):
        pass

    def process(self, cloudPoints, radius = 0.2):
        
        print(cloudPoints.shape)

        points = IndexKD(cloudPoints)
        
        reduced = cloudPoints[list(filters.ball(points, radius))]

        print(reduced.shape)

        return reduced