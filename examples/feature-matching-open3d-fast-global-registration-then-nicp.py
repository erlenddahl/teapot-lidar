import open3d as o3d
import numpy as np
import copy
import time

import sys
sys.path.append('..')
from pcapReader import PcapReader

def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])

    source_temp.transform(transformation)
    
    # create point cloud and coordinate axes geometries
    axes = o3d.geometry.TriangleMesh.create_coordinate_frame(1.0)

    # initialize visualizer and rendering options
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    for g in [source_temp, target_temp]:
        vis.add_geometry(g)

    vis.add_geometry(axes)
    ropt = vis.get_render_option()
    ropt.point_size = 1.0
    ropt.background_color = np.asarray([0, 0, 0])

    # initialize camera settings
    ctr = vis.get_view_control()
    ctr.set_zoom(0.1)
    ctr.set_lookat([0, 0, 0])
    ctr.set_up([0.85, 0.12, 0.52])

    # run visualizer main loop
    print("Press Q or Excape to exit")
    vis.run()
    vis.destroy_window()

def preprocess_point_cloud(pcd, voxel_size):

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def execute_fast_global_registration(source_down, target_down, source_fpfh,
                                     target_fpfh, voxel_size):
    distance_threshold = voxel_size * 0.5
    print(":: Apply fast global registration with distance threshold %.3f" \
            % distance_threshold)
    result = o3d.pipelines.registration.registration_fast_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))
    return result

if __name__ == "__main__":

    reader = PcapReader.fromPathArgs()

    source = reader.readFrameAsPointCloud(20, True)
    target = reader.readFrameAsPointCloud(25, True)
    
    accumulatedTime = 0.0

    print("Preparing data (downsampling, generating FPFH vectors)")
    startTime = time.perf_counter()
    voxel_size = 0.05
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)
    accumulatedTime += time.perf_counter() - startTime
    print(f"Time usage: {time.perf_counter() - startTime:0.4f} seconds.")
    print("")

    startTime = time.perf_counter()
    result_ransac = execute_fast_global_registration(source_down, target_down,
                                            source_fpfh, target_fpfh,
                                            voxel_size)
    accumulatedTime += time.perf_counter() - startTime
    print(f"Downsampling (0.5) performed in {(time.perf_counter() - startTime)/2.0:0.4f} seconds per cloud.")
    print(result_ransac)
    draw_registration_result(source_down, target_down, result_ransac.transformation)

    threshold = 1
    trans_init = result_ransac.transformation

    print("Apply point-to-plane ICP")
    startTime = time.perf_counter()
    reg_p2l = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))
    accumulatedTime += time.perf_counter() - startTime
    print(f"Time usage: {time.perf_counter() - startTime:0.4f} seconds.")
    print(reg_p2l)
    print("Transformation is:")
    print(reg_p2l.transformation)
    print("Transformed center:")
    print(o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(reg_p2l.transformation).get_center())
    print("")

    draw_registration_result(source_down, target_down, result_ransac.transformation)

    print(f"Accumulated time: {accumulatedTime:0.4f} seconds.")