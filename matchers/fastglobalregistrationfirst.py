import numpy as np
import open3d as o3d

from matchers.nicp import NicpMatcher

class FastGlobalFirstNicpMatcher:

    def __init__(self, voxel_size = 0.5):

        self.pure_nicp = NicpMatcher()
        self.voxel_size = voxel_size

    def preprocess_point_cloud(self, pcd, voxel_size):

        radius_normal = voxel_size * 2
        pcd.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

        pcd_down = pcd.voxel_down_sample(voxel_size)

        radius_feature = voxel_size * 5
        pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(pcd_down,
            o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
        return pcd_down, pcd_fpfh

    def execute_fast_global_registration(self, source_down, target_down, source_fpfh,
                                        target_fpfh, voxel_size):
        distance_threshold = voxel_size * 0.5
        print(":: Apply fast global registration with distance threshold %.3f" \
                % distance_threshold)
        result = o3d.pipelines.registration.registration_fast_based_on_feature_matching(
            source_down, target_down, source_fpfh, target_fpfh,
            o3d.pipelines.registration.FastGlobalRegistrationOption(
                maximum_correspondence_distance=distance_threshold))
        return result

    def match(self, source, target):

        # Initialize an initial transformation. This is meant to be a
        # rough transformation to align the frames, which we find by
        # running a global registration first.
        voxel_size = 0.05
        source_down, source_fpfh = self.preprocess_point_cloud(source, voxel_size)
        target_down, target_fpfh = self.preprocess_point_cloud(target, voxel_size)

        result_ransac = self.execute_fast_global_registration(source_down, target_down,
                                                source_fpfh, target_fpfh,
                                                voxel_size)

        threshold = 1
        trans_init = result_ransac.transformation

        # Run NICP
        threshold = 1
        reg_p2l = o3d.pipelines.registration.registration_icp(
            source, target, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))

        return reg_p2l