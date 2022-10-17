import numpy as np
import open3d as o3d

class NicpMatcher:

    def match(self, source, target, threshold = 1, trans_init = None):

        # Initialize an initial transformation. This is meant to be a
        # rough transformation to align the frames, but as lidar frames
        # are roughly aligned anyway, we use the identity matrix.
        if trans_init is None:
            trans_init = np.identity(4)

        # Run NICP
        reg_p2l = o3d.pipelines.registration.registration_icp(
            source, target, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))

        return reg_p2l