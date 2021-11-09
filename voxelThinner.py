from voxelize import voxelize
import numpy as np

class VoxelThinner:

    def __init__(self):
        pass

    def process(self, cloudPoints):
        
        print(cloudPoints.shape)
        
        # TODO: Optimize this
        bbox = [min([x[0] for x in cloudPoints]), min([x[1] for x in cloudPoints]), min([x[2] for x in cloudPoints]), max([x[0] for x in cloudPoints]), max([x[1] for x in cloudPoints]), max([x[2] for x in cloudPoints])]

        voxels, _, _ = voxelize(
            cloudPoints,
            voxel_size=np.array([0.2, 0.2, 0.2]),
            grid_range=np.array(bbox),
            max_num_voxels=len(cloudPoints) // 3
        )

        print(voxels.shape)

        return voxels