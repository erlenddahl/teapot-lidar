import time
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

import sys
sys.path.append('..')
from pcapReader import PcapReader

from pyoints import (
    transformation,
    filters,
    registration,
    indexkd
)

# Configure PCAP and JSON file paths
reader = PcapReader.fromPathArgs()

A = reader.readFrame(20)
B = reader.readFrame(25)

print(A.shape)
print(B.shape)

r = 0.2
startTime = time.perf_counter()
A = A[list(filters.ball(indexkd.IndexKD(A), r))]
B = B[list(filters.ball(indexkd.IndexKD(B), r))]
print(f"Ball filtering performed in {(time.perf_counter() - startTime)/2.0:0.4f} seconds per cloud.")

def visualizeGeometries(geometries):

    # create point cloud and coordinate axes geometries
    axes = o3d.geometry.TriangleMesh.create_coordinate_frame(1.0)

    # initialize visualizer and rendering options
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    for g in geometries:
        vis.add_geometry(o3d.geometry.PointCloud(o3d.utility.Vector3dVector(g.reshape((-1, 3)))))

    vis.add_geometry(axes)
    ropt = vis.get_render_option()
    ropt.point_size = 1.0
    ropt.background_color = np.asarray([0, 0, 0])

    # initialize camera settings
    ctr = vis.get_view_control()
    ctr.set_zoom(0.1)
    ctr.set_lookat([0, 0, 0])
    ctr.set_up([1, 0, 0])

    # run visualizer main loop
    print("Press Q or Excape to exit")
    vis.run()
    vis.destroy_window()

visualizeGeometries([A, B])

coords_dict = {
    'A': A,
    'B': B,
}

d_th = 2
radii = [d_th, d_th, d_th]

startTime = time.perf_counter()

icp = registration.ICP(
    radii,
    max_iter=100,
    max_change_ratio=0.00001,
    k=1
)

T_dict, pairs_dict, report = icp(coords_dict)

print(f"ICP adjustments performed in {time.perf_counter() - startTime:0.4f} seconds.")

A = transformation.transform(coords_dict["A"], T_dict["A"])
B = transformation.transform(coords_dict["B"], T_dict["B"])

visualizeGeometries([A, B])

fig = plt.figure(figsize=(15, 8))
plt.xlim(0, len(report['RMSE']) + 1)
plt.xlabel('Iteration')
plt.ylabel('RMSE')

plt.bar(np.arange(len(report['RMSE']))+1, report['RMSE'], color='gray')
plt.show()