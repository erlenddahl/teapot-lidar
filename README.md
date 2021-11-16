# TEAPOT LIDAR
This repo will contain relevant code for working with LIDAR data in the SINTEF project TEAPOT.

## Requirements
The code is implemented and tested with Python 3.6 because of limitations with some of the libraries. 

Create a new Anaconda environment (or use an existing, or venv, or whatever):
```
conda create -n teapot python=3.6
conda activate teapot
```

Install the Python requirements using pip:

```
pip install -r requirements.txt
```

## Running the code

### PcapBrowser
The most general entry point is pcapBrowser.py, a simple open3d visualization of the point cloud with arrow navigation and cloud thinning, which can be run like this:

```
python pcapBrowser.py --pcap path\to\pcap-file.pcap --json path\to\metadata-file.json
```

Or, if the pcap and json files have the same names (123.pcap and 123.json), it is sufficient to use the pcap parameter:

```
python pcapBrowser.py --pcap path\to\pcap-file.pcap
```

Note: be wary of spaces in the paths (surround them with quotes).

When the visualization window appears, use the arrow keys to navigate from frame to frame, and P to move through the different cloud processors (None, voxel thinner or ball thinner).
