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

### Navigator
navigator.py runs through all frames the given PCAP file, and uses the selected registration algorithm to place all frames in the same coordinate system. The vehicle's movements between frames are calculated and visualized as a red line in the final point cloud. Data can be previewed using the --preview argument, and/or saved using the --save-to argument. For debugging, the --frames argument sets a maximum number of frames to be read before finishing, and the --skip-frames argument allows for simulating lower frequencies.

Example with default preview and no saving:
```
python pcapBrowser.py --pcap path\to\pcap-file.pcap --json path\to\metadata-file.json
```

Example with no preview, save results:
```
python pcapBrowser.py --pcap path\to\pcap-file.pcap --json path\to\metadata-file.json --preview never --save-to results\[pcap]_[time]
```

Full argument description:
```
usage: navigator.py [-h] --pcap PCAP [--json JSON] [--frames FRAMES]
                    [--skip-frames SKIP_FRAMES] [--preview {always,end,never}]
                    [--save-to SAVE_TO]

optional arguments:
  -h, --help            show this help message and exit
  --pcap PCAP           The path to the PCAP file to visualize, relative or
                        absolute.
  --json JSON           The path to the corresponding JSON file with the
                        sensor metadata, relative or absolute. If this is not
                        given, the PCAP location is used (by replacing .pcap
                        with .json).
  --frames FRAMES       If given a number larger than 1, only this many frames
                        will be read from the PCAP file.
  --skip-frames SKIP_FRAMES
                        If given a positive number larger than 0, this many
                        frames will be skipped between every frame read from
                        the PCAP file.
  --preview {always,end,never}
                        Show constantly updated point cloud and data plot
                        previews while processing ('always'), show them only
                        at the end ('end'), or don't show them at all
                        ('never').
  --save-to SAVE_TO     If given, final results will be stored at this path.
                        The path will be used for all types of results, with
                        appendices depending on file type ('_data.json',
                        '_plot.png', '_cloud.laz'). The path can include
                        "[pcap]" and/or "[time]" which will be replaced with
                        the name of the parsed PCAP file and the time of
                        completion respectively.
```

### PcapBrowser
pcapBrowser.py is a very simple open3d based tool for visualizing the frames in a PCAP file. It allows you to browse the frames using the arrow keys on the keyboard, and can be run like this:

```
python pcapBrowser.py --pcap path\to\pcap-file.pcap --json path\to\metadata-file.json
```

Or, if the pcap and json files have the same names (123.pcap and 123.json), it is sufficient to use the pcap parameter:

```
python pcapBrowser.py --pcap path\to\pcap-file.pcap
```

Note: be wary of spaces in the paths (surround them with quotes).

When the visualization window appears, use the arrow keys to navigate from frame to frame, and P to move through the different cloud processors (None, voxel thinner or ball thinner).
