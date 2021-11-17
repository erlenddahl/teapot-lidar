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

    A = reader.readFrame(20)
    B = reader.readFrame(25)
    
    # Remove the vehicle, which is always stationary at the center. We don't want that
    # to interfere with the point cloud alignment.
    vr = 2.5
    A = A[((A[:, 0] > vr) | (A[:, 0] < -vr)) | ((A[:, 1] > vr) | (A[:, 1] < -vr))]
    B = B[((B[:, 0] > vr) | (B[:, 0] < -vr)) | ((B[:, 1] > vr) | (B[:, 1] < -vr))]

    source = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(A))
    target = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(B))

    startTime = time.perf_counter()
    source = source.voxel_down_sample(voxel_size=0.5)
    target = target.voxel_down_sample(voxel_size=0.5)
    print(f"Downsampling (0.5) performed in {(time.perf_counter() - startTime)/2.0:0.4f} seconds per cloud.")

    threshold = 1
    trans_init = np.identity(4)
    #draw_registration_result(source, target, trans_init)
    print("Initial alignment")
    evaluation = o3d.pipelines.registration.evaluate_registration(source, target, threshold, trans_init)
    print(evaluation)

    print("Apply point-to-point ICP")
    startTime = time.perf_counter()
    reg_p2p = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))
    print(f"Time usage: {time.perf_counter() - startTime:0.4f} seconds.")
    print(reg_p2p)
    print("Transformation is:")
    print(reg_p2p.transformation)
    print("")
    print("Transformed center:")
    print(o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(reg_p2p.transformation).get_center())
    draw_registration_result(source, target, reg_p2p.transformation)

    print("Estimating normals")
    startTime = time.perf_counter()
    source.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    target.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    print(f"Time usage: {time.perf_counter() - startTime:0.4f} seconds.")
    print("")

    print("Apply point-to-plane ICP")
    startTime = time.perf_counter()
    reg_p2l = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))
    print(f"Time usage: {time.perf_counter() - startTime:0.4f} seconds.")
    print(reg_p2l)
    print("Transformation is:")
    print(reg_p2l.transformation)
    print("Transformed center:")
    print(o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(reg_p2l.transformation).get_center())
    print("")
    draw_registration_result(source, target, reg_p2l.transformation)