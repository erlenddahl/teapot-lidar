from pyoints.ballfilter import ball
from pyoints.indexkd import IndexKD

class VoxelThinnerPyoints:

    def __init__(self):
        pass

    def process(self, cloudPoints):
        
        print(cloudPoints.shape)

        points = IndexKD(cloudPoints)
        
        reduced = cloudPoints[list(ball(points, 0.2))]

        print(reduced.shape)

        return reduced