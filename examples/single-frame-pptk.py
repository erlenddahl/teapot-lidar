import pptk
from ouster import client, pcap
from contextlib import closing
from more_itertools import nth

# Configure PCAP and JSON file paths
pathBase = "..\\data\\2021-10-05 - Honefoss med parkeringshus\\OS-1-128_992035000186_1024x10_20211005_134603"
pcapPath = pathBase + ".pcap"
metaDataPath = pathBase + ".json"

# Read the metadata from the JSON file.
with open(metaDataPath, "r") as f:
	metadata = client.SensorInfo(f.read())

# Open the LIDAR data source from the PCAP file
source = pcap.Pcap(pcapPath, metadata)

# Read the 50th LIDAR frame
with closing(client.Scans(source)) as scans:
    scan = nth(scans, 50)

# Create a function that translates coordinates to a plottable coordinate system
xyzlut = client.XYZLut(source.metadata)
xyz = xyzlut(scan)

# Extract some relevant attributes that can be used to color the plot
attr1 = scan.field(client.ChanField.RANGE)[:, :, None]
attr2 = scan.field(client.ChanField.REFLECTIVITY)[:, :, None]
attr3 = scan.field(client.ChanField.NEAR_IR)[:, :, None]
attr4 = scan.field(client.ChanField.SIGNAL)[:, :, None]

# Create a PPTK viewer to show the data
poc = pptk.viewer(xyz)
poc.attributes(attr1, attr2, attr3, attr4)
poc.set(point_size=0.005)
