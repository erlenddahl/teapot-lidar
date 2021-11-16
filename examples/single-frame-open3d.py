from ouster import client, pcap
from more_itertools import nth
import numpy as np

# Configure PCAP and JSON file paths
pathBase = "..\\data\\2021-10-05 - Honefoss med parkeringshus\\OS-1-128_992035000186_1024x10_20211005_134603"
pcapPath = pathBase + ".pcap"
metaDataPath = pathBase + ".json"

# Read the metadata from the JSON file.
with open(metaDataPath, "r") as f:
	metadata = client.SensorInfo(f.read())

# Open the LIDAR data source from the PCAP file
source = pcap.Pcap(pcapPath, metadata)

# Function taken from ouster-sdk-examples:

def pcap_3d_one_scan(source: client.PacketSource,
                     metadata: client.SensorInfo,
                     num: int = 0) -> None:
    """Render one scan from a pcap file in the Open3D viewer.

    Args:
        pcap_path: path to the pcap file
        metadata_path: path to the .json with metadata (aka :class:`.SensorInfo`)
        num: scan number in a given pcap file (satrs from *0*)
    """
    import open3d as o3d

    # get single scan by index
    scan = nth(client.Scans(source), num)

    if not scan:
        print(f"ERROR: Scan # {num} in not present in pcap file")
        exit(1)

    # compute point cloud using client.SensorInfo and client.LidarScan
    xyz = client.XYZLut(metadata)(scan)

    # create point cloud and coordinate axes geometries
    cloud = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(xyz.reshape((-1, 3))))
    axes = o3d.geometry.TriangleMesh.create_coordinate_frame(1.0)

    # initialize visualizer and rendering options
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(cloud)
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

pcap_3d_one_scan(source, metadata, 50)