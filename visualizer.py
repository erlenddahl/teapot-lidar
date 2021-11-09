import pptk
from ouster import client, pcap
from contextlib import closing
from more_itertools import nth
import open3d as o3d
import numpy as np

# Configure PCAP and JSON file paths
pathBase = "data\\2021-10-05 - Honefoss med parkeringshus\\OS-1-128_992035000186_1024x10_20211005_134603"
pcapPath = pathBase + ".pcap"
metaDataPath = pathBase + ".json"

# Read the metadata from the JSON file.
with open(metaDataPath, "r") as f:
	metadata = client.SensorInfo(f.read())

# Open the LIDAR data source from the PCAP file
source = None
def openSource():
    global source
    source = pcap.Pcap(pcapPath, metadata)

openSource()

def printInfo():
    for packet in source:
        if isinstance(packet, client.LidarPacket):
            # Now we can process the LidarPacket. In this case, we access
            # the encoder_counts, timestamps, and ranges
            encoder_counts = packet.header(client.ColHeader.ENCODER_COUNT)
            timestamps = packet.header(client.ColHeader.TIMESTAMP)
            ranges = packet.field(client.ChanField.RANGE)
            print(f'  encoder counts = {encoder_counts.shape}')
            print(f'  timestamps = {timestamps.shape}')
            print(f'  ranges = {ranges.shape}')

        elif isinstance(packet, client.ImuPacket):
            # and access ImuPacket content
            print(f'  acceleration = {packet.accel}')
            print(f'  angular_velocity = {packet.angular_vel}')

xyzLut = client.XYZLut(metadata)

# Create a simple axis visualization
axes = o3d.geometry.TriangleMesh.create_coordinate_frame(1.0)

# initialize visualizer and rendering options
vis = o3d.visualization.VisualizerWithKeyCallback()
vis.create_window()
vis.add_geometry(axes)
ropt = vis.get_render_option()
ropt.point_size = 1.0
ropt.background_color = np.asarray([0, 0, 0])

# initialize camera settings
ctr = vis.get_view_control()

def reset_view():
    global ctr
    ctr.set_zoom(0.1)
    ctr.set_lookat([0, 0, 0])
    ctr.set_up([1, 0, 0])

currentFrame = 0
currentGeometry = None

def setFrame(num:int):

    global currentGeometry
    global currentFrame

    newGeometry = readFrameGeometry(num)
    if newGeometry is None:
        return False
    
    if currentGeometry is not None:
        vis.remove_geometry(currentGeometry, False)

    vis.add_geometry(newGeometry, num == 0)

    currentGeometry = newGeometry
    currentFrame = num

    print("Showing frame ", num)
    return True

readFrames = []
def readFrameGeometry(num:int):

    global readFrames

    if num < 0:
        return None

    while len(readFrames) < num + 1:
        scan = nth(client.Scans(source), 1)

        if scan is None:
            readFrames.append(None)
        else:
            xyz = xyzLut(scan)
            readFrames.append(o3d.geometry.PointCloud(o3d.utility.Vector3dVector(xyz.reshape((-1, 3)))))

    return readFrames[num]

def key_exit(vis):
    vis.destroy_window()

def key_next(vis):
    global currentFrame
    currentFrame += 1
    if not setFrame(currentFrame):
        currentFrame -= 1

def key_prev(vis):
    global currentFrame
    currentFrame -= 1
    if not setFrame(currentFrame):
        currentFrame += 1

vis.register_key_callback(262, key_next) # Arrow right
vis.register_key_callback(263, key_prev) # Arrow left
# List of key codes can be found here: https://www.glfw.org/docs/latest/group__keys.html

setFrame(0)
reset_view()

# run visualizer main loop
print("Press Q or Excape to exit")

vis.run()
vis.destroy_window()
