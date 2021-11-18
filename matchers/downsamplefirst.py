import numpy as np
import open3d as o3d

from matchers.nicp import NicpMatcher

class DownsampleFirstNicpMatcher:

    def __init__(self, voxel_size = 0.5):

        self.pure_nicp = NicpMatcher()
        self.voxel_size = voxel_size

    def match(self, source, target):

        # Initialize an initial transformation. This is meant to be a
        # rough transformation to align the frames, which we find by
        # running on a downsampled variant first.
        reg = self.pure_nicp.match(source.voxel_down_sample(voxel_size=self.voxel_size), target.voxel_down_sample(voxel_size=self.voxel_size))
        trans_init = reg.transformation

        # Run NICP
        threshold = 1
        reg_p2l = o3d.pipelines.registration.registration_icp(
            source, target, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))

        return reg_p2l