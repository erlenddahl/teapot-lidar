import numpy as np
from numpy.lib.utils import source
import open3d as o3d
import time
import sys
sys.path.append('..')
from pcapReaderHelper import PcapReaderHelper

def pairwise_registration(source, target, max_correspondence_distance_coarse,
                      max_correspondence_distance_fine):
    icp_coarse = o3d.pipelines.registration.registration_icp(
        source, target, max_correspondence_distance_coarse, np.identity(4),
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    icp_fine = o3d.pipelines.registration.registration_icp(
        source, target, max_correspondence_distance_fine,
        icp_coarse.transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    transformation_icp = icp_fine.transformation
    information_icp = o3d.pipelines.registration.get_information_matrix_from_point_clouds(
        source, target, max_correspondence_distance_fine,
        icp_fine.transformation)
    return transformation_icp, information_icp


def full_registration(pcds, max_correspondence_distance_coarse,
                      max_correspondence_distance_fine):
    pose_graph = o3d.pipelines.registration.PoseGraph()
    odometry = np.identity(4)
    pose_graph.nodes.append(o3d.pipelines.registration.PoseGraphNode(odometry))
    n_pcds = len(pcds)
    for source_id in range(n_pcds):
        for target_id in range(source_id + 1, n_pcds):#min(n_pcds, source_id + 10)): #n_pcds):#
            transformation_icp, information_icp = pairwise_registration(
                pcds[source_id], pcds[target_id], max_correspondence_distance_coarse,
                      max_correspondence_distance_fine)
            print("Build o3d.pipelines.registration.PoseGraph " + str(source_id) + ", " + str(target_id))
            if target_id == source_id + 1:  # odometry case
                odometry = np.dot(transformation_icp, odometry)
                pose_graph.nodes.append(
                    o3d.pipelines.registration.PoseGraphNode(
                        np.linalg.inv(odometry)))
                pose_graph.edges.append(
                    o3d.pipelines.registration.PoseGraphEdge(source_id,
                                                             target_id,
                                                             transformation_icp,
                                                             information_icp,
                                                             uncertain=False))
            else:  # loop closure case
                pose_graph.edges.append(
                    o3d.pipelines.registration.PoseGraphEdge(source_id,
                                                             target_id,
                                                             transformation_icp,
                                                             information_icp,
                                                             uncertain=True))
    return pose_graph

print("Read all frames")
startTime = time.perf_counter()
voxel_size = 0.02
reader = PcapReaderHelper.from_path_args()
pcds = reader.read_all_frames(True)
print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

print("Downsample frames")
startTime = time.perf_counter()
pcds_down = [x.voxel_down_sample(voxel_size=voxel_size) for x in pcds]
print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

print("Estimate normals")
startTime = time.perf_counter()
for pcd in pcds_down:
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

print("Perform full registration")
startTime = time.perf_counter()
max_correspondence_distance_coarse = voxel_size * 15
max_correspondence_distance_fine = voxel_size * 1.5
pose_graph = full_registration(pcds_down,
                                max_correspondence_distance_coarse,
                                max_correspondence_distance_fine)
print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

print("Optimizing PoseGraph ...")
startTime = time.perf_counter()
option = o3d.pipelines.registration.GlobalOptimizationOption(
    max_correspondence_distance=max_correspondence_distance_fine,
    edge_prune_threshold=0.25,
    reference_node=0)
with o3d.utility.VerbosityContextManager(
        o3d.utility.VerbosityLevel.Debug) as cm:
    o3d.pipelines.registration.global_optimization(
        pose_graph,
        o3d.pipelines.registration.GlobalOptimizationLevenbergMarquardt(),
        o3d.pipelines.registration.GlobalOptimizationConvergenceCriteria(),
        option)
print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

print("Transform points and display")
startTime = time.perf_counter()
for point_id in range(len(pcds_down)):
    pcds_down[point_id].transform(pose_graph.nodes[point_id].pose)
o3d.visualization.draw_geometries(pcds_down)
print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

print("Combine point cloud")
startTime = time.perf_counter()
reader = PcapReaderHelper.from_path_args()
pcds = reader.read_all_frames(True)
pcd_combined = o3d.geometry.PointCloud()
for point_id in range(len(pcds)):
    pcds[point_id].transform(pose_graph.nodes[point_id].pose)
    pcd_combined += pcds[point_id]
pcd_combined_down = pcd_combined.voxel_down_sample(voxel_size=voxel_size)
print(f"    > Time usage: {time.perf_counter() - startTime:0.4f} seconds.")

o3d.io.write_point_cloud("multiway_registration.pcd", pcd_combined_down)
o3d.visualization.draw_geometries([pcd_combined_down])