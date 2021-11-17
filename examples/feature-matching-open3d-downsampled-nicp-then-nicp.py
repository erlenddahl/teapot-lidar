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

if __name__ == "__main__":

    reader = PcapReader.fromPathArgs()

    source = reader.readFrameAsPointCloud(20, True)
    target = reader.readFrameAsPointCloud(25, True)

    accumulatedTime = 0.0

    print("Estimating normals")
    startTime = time.perf_counter()
    source.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    target.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    accumulatedTime += time.perf_counter() - startTime
    print(f"Time usage: {time.perf_counter() - startTime:0.4f} seconds.")
    print("")

    startTime = time.perf_counter()
    downsampled_source = source.voxel_down_sample(voxel_size=0.5)
    downsampled_target = target.voxel_down_sample(voxel_size=0.5)
    accumulatedTime += time.perf_counter() - startTime
    print(f"Downsampling (0.5) performed in {(time.perf_counter() - startTime)/2.0:0.4f} seconds per cloud.")

    threshold = 1
    trans_init = np.identity(4)

    draw_registration_result(downsampled_source, downsampled_target, trans_init)

    print("Apply point-to-plane ICP")
    startTime = time.perf_counter()
    reg_p2l = o3d.pipelines.registration.registration_icp(
        downsampled_source, downsampled_target, threshold, trans_init,
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

    trans_init = reg_p2l.transformation

    draw_registration_result(downsampled_source, downsampled_target, trans_init)

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
    draw_registration_result(source, target, reg_p2l.transformation)

    print(f"Accumulated time: {accumulatedTime:0.4f} seconds.")