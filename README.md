# TEAPOT LIDAR
This repo will contain relevant code for working with [lidar](https://en.wikipedia.org/wiki/Lidar) data in the [SINTEF](https://www.sintef.no) project [TEAPOT](https://www.sintef.no/prosjekter/2021/teapot/).

In this project we will investigate if the lidar data can be used to improve or replace GNSS navigation in two different ways: a) by "incremental navigation", that is by calculating vehicle movements by the difference between sequential lidar frames, and b) by using a georeferenced point cloud to locate a lidar frame.

During the TEAPOT project, LiDAR data was collected from four different locations with and without snow and analyzed using the two nagivation methods outlined below. Analysis results can be found [here](https://github.com/erlenddahl/teapot-lidar/blob/main/validation/_notes/summary.md).

## Incremental navigation (visual odometry)
Incremental navigation works by using [point cloud registration](https://en.wikipedia.org/wiki/Point_set_registration) to calculate a transformation to align two sequential frames from a lidar dataset. This transformation can then be used to calculate how far and in which direction the vehicle moved between these two frames. By doing this for every frame pair in a lidar dataset, we can calculate the total movement. Given an initial GNSS position, the idea is that we can calculate updated GNSS positions throughout the movement without any more GNSS data. This is equal to a simple visual odometry.

| Two sequential frames with a visible difference are aligned by point cloud registration | An animation showing the alignment process frame by frame | The final point cloud with a movement path (red line)
|-----|-----|-----
| [<img src="./notes/frame-matching-test-frames-cropped.png" width="300" height="150" />](./notes/frame-matching-test-frames-cropped.png) | [<img src="./notes/animation_tiny.gif" width="300" height="150" />](./notes/animation.gif) | [<img src="./notes/navigated_point_cloud_example.jpg" width="300" height="150" />](./notes/navigated_point_cloud_example.jpg)

More details can be found in the [technical notes](./notes/notes.md).

## Georeferenced point cloud navigation
Georeferenced navigation (also called "absolute navigation" other places in this repo) means that each lidar frame is registered against an existing pointcloud from the target location, putting the frame directly into a georeferenced location. This gives the position of the frame (and thus the vehicle that is in the center of the frame) directly. Due to constraints in the registration algorithms, it is not feasible to register a frame against a large pointcloud, so there is an intermediate step that extracts a frame-sized part of the cloud around the current location (known or estimated), then registers against that.

_[Images to come.]_

# Running the code

## Requirements
The code is implemented and tested with Python 3.6 because of limitations with some of the libraries. 

Create a new Anaconda environment (or use an existing, or venv, or whatever), and install the requirements:
```
conda create --name teapot310 python=3.10.9
conda activate teapot310
pip install open3d numpy matplotlib tqdm laspy[laszip] ouster-sdk[examples] tabulate probreg pyproj
```

## Utilities

### Browsing PCAP files
pcapBrowser.py is a very simple open3d based tool for visualizing the frames in a PCAP file. It allows you to browse the frames using the arrow keys on the keyboard, and can be run like this:

```
python pcapBrowser.py --pcap path\to\pcap-file.pcap --json path\to\metadata-file.json

# Or, if the pcap and json files have the same names (123.pcap and 123.json), it is sufficient to use the pcap parameter:
python pcapBrowser.py --pcap path\to\pcap-file.pcap
```

Note: be wary of spaces in the paths (surround them with quotes).

When the visualization window appears, use the arrow keys to navigate from frame to frame, and P to move through the different cloud processors (None, voxel thinner or ball thinner). Pressing the I key prints detailed information about this frame.

### Point cloud generation
The pointCloud.py script reads a folder of .laz files, and combines them into one large point cloud, which is saved as a Open3D .pcd file. Due to float rounding issues, the .laz files are first read once (header only) to generate a common minimum, and then all .laz files are translated towards the origin using this minimum so that the absolute value of all point coordinates are low numbers, thus less vulnerable to float rounding imprecision. Because of this, an additional metadata file is stored with information about how much the cloud was translated (this can be used to convert the "origin-local" coordinates back to original coordinates while running navigation).

```
# Example of combining .laz files into a single .pcd:
python pointCloud.py --create-from "folder-with-laz-files" --preview never --write-to "full-point-cloud.pcd"

# Example of visualizing a .pcd point cloud:
python pointCloud.py --show "full-point-cloud.pcd"
```

**Full argument description:**
```
usage: pointCloud.py [-h] [--create-from CREATE_FROM] [--preview {always,end,never}] [--max-files MAX_FILES]
                     [--write-to WRITE_TO] [--show SHOW]

options:
  -h, --help            show this help message and exit
  --create-from CREATE_FROM
                        A directory containing the point cloud as .laz files.
  --preview {always,end,never}
                        Show constantly updated point cloud and data plot previews while processing ('always'), show
                        them only at the end ('end'), or don't show them at all ('never').
  --max-files MAX_FILES
                        Stop reading after the given number of files (useful for saving time while testing).
  --write-to WRITE_TO   Write the assembled point cloud to this location.
  --show SHOW           A .pcd file to show -- will not do any processing, just show it.
```

## Incremental navigation
incrementalNavigator.py runs through all frames the given PCAP file, and uses the selected registration algorithm to place all frames in the same coordinate system. The vehicle's movements between frames are calculated and visualized as a red line in the final point cloud. Data can be previewed using the --preview argument, and/or saved using the --save-to argument. For debugging, the --frames argument sets a maximum number of frames to be read before finishing, and the --skip-every-frame argument allows for simulating lower frequencies by skipping for example every second frame. The --skip-start or --skip-until-[x/y/radius] arguments can be used to skip processing until the vehicle reaches a certain point in the route. For comparisons against the actual driving route, the --sbet argument can be used to provide the actual GNSS coordinates.

```
# Example with default preview and no saving:
python incrementalNavigator.py --pcap path\to\pcap-file.pcap --json path\to\metadata-file.json

# Example with default metadata file, no preview, and results saved to the results folder:
python incrementalNavigator.py --pcap path\to\pcap-file.pcap --preview never --save-to "results_folder"

# Example with multiple .pcap files:
python incrementalNavigator.py --pcap path\to\pcap-file1.pcap path\to\pcap-file2.pcap --preview never --save-to "results_folder"

# Example with all .pcap files the given folder:
python incrementalNavigator.py --pcap path\to\folder_with_pcaps --preview never --save-to "results_folder"

# Example with various settings for when to start the navigation, and when to end it (when the error gets too big):
python incrementalNavigator.py --pcap "validation\Lillehammer\211021\pcap\4_10hz" --preview always --sbet "validation\Lillehammer\211021\navigasjon\sbet-output-UTC-1000.out" --sbet-z-offset -39.416 --skip-start 0 --build-cloud-after 0 --save-to "validation\results\incremental\Lillehammer\211021\4_10hz" --skip-until-x 579490.13 --skip-until-y 6776060.22
```

**Full argument description:**
```
usage: incrementalNavigator.py [-h] --pcap PCAP [PCAP ...] [--json JSON [JSON ...]] [--sbet SBET]
                               [--sbet-z-offset SBET_Z_OFFSET] [--recreate-caches] [--algorithm ALGORITHM]
                               [--frames FRAMES] [--build-cloud-after BUILD_CLOUD_AFTER]
                               [--skip-every-frame SKIP_EVERY_FRAME] [--skip-until-radius SKIP_UNTIL_RADIUS]
                               [--skip-until-x SKIP_UNTIL_X] [--skip-until-y SKIP_UNTIL_Y] [--skip-start SKIP_START]
                               [--voxel-size VOXEL_SIZE] [--downsample-after DOWNSAMPLE_AFTER]
                               [--preview {always,end,never}] [--save-to SAVE_TO]
                               [--save-screenshots-to SAVE_SCREENSHOTS_TO] [--save-frame-pairs-to SAVE_FRAME_PAIRS_TO]
                               [--save-frame-pair-threshold SAVE_FRAME_PAIR_THRESHOLD]
                               [--skip-last-frame-in-pcap-file SKIP_LAST_FRAME_IN_PCAP_FILE]
                               [--raise-on-error RAISE_ON_ERROR] [--raise-on-movement RAISE_ON_MOVEMENT]
                               [--wait-after-initial-frame WAIT_AFTER_INITIAL_FRAME]

options:
  -h, --help            show this help message and exit
  --pcap PCAP [PCAP ...]
                        The path to one or more PCAP files to visualize, relative or absolute. A path to a directory
                        containing multiple pcap files can also be provided.
  --json JSON [JSON ...]
                        The path to corresponding JSON file(s) for each of the PCAP file(s) with the sensor metadata,
                        relative or absolute. If this is not given, the PCAP location is used (by replacing .pcap with
                        .json). A path to a directory containing multiple json files can also be provided.
  --sbet SBET           The path to a corresponding SBET file with GNSS coordinates.
  --sbet-z-offset SBET_Z_OFFSET
                        If the GNSS positions in the SBET file have an altitude offset from the point cloud, this
                        argument will be added/subtracted on the Z coordinates of each SBET coordinate.
  --recreate-caches
  --algorithm ALGORITHM
                        Use this registration algorithm (see names in algorithmHelper.py).
  --frames FRAMES       If given a number larger than 1, only this many frames will be read from the PCAP file.
  --build-cloud-after BUILD_CLOUD_AFTER
                        How often registered frames should be added to the generated point cloud. 0 or lower
                        deactivates the generated point cloud. 1 or higher generates a point cloud with details (and
                        time usage) decreasing with higher numbers.
  --skip-every-frame SKIP_EVERY_FRAME
                        If given a positive number larger than 0, this many frames will be skipped between every frame
                        read from the PCAP file.
  --skip-until-radius SKIP_UNTIL_RADIUS
                        If given together with --skip-until-x and --skip-until-y, the analysis will skip frames until
                        the actual position enters the circle given by these three parameters.
  --skip-until-x SKIP_UNTIL_X
                        If given together with --skip-until-x and --skip-until-radius, the analysis will skip frames
                        until the actual position enters the circle given by these three parameters.
  --skip-until-y SKIP_UNTIL_Y
                        If given together with --skip-until-y and --skip-until-radius, the analysis will skip frames
                        until the actual position enters the circle given by these three parameters.
  --skip-start SKIP_START
                        If given a positive number larger than 0, this many frames will be skipped before starting
                        processing frames.
  --voxel-size VOXEL_SIZE
                        The voxel size used for cloud downsampling. If less than or equal to zero, downsampling will
                        be disabled.
  --downsample-after DOWNSAMPLE_AFTER
                        The cloud will be downsampled (which is an expensive operation for large clouds, so don't do
                        it too often) after this many registered frames have been added. If this number is higher than
                        the number of frames being read, it will be downsampled once at the end of the process (unless
                        downsampling is disabled, see --voxel-size).
  --preview {always,end,never}
                        Show constantly updated point cloud and data plot previews while processing ('always'), show
                        them only at the end ('end'), or don't show them at all ('never').
  --save-to SAVE_TO     If given, final results will be stored in this folder.
  --save-screenshots-to SAVE_SCREENSHOTS_TO
                        If given, point cloud screenshots will be saved in this directory with their indices as
                        filenames (0.png, 1.png, 2.png, etc). Only works if --preview is set to 'always'.
  --save-frame-pairs-to SAVE_FRAME_PAIRS_TO
                        If given, frame pairs with a registered fitness below --save-frame-pair-threshold will be
                        saved to the given directory for manual inspection.
  --save-frame-pair-threshold SAVE_FRAME_PAIR_THRESHOLD
                        If --save-frame-pairs-to is given, frame pairs with a registered fitness value below this
                        value will be saved.
  --skip-last-frame-in-pcap-file SKIP_LAST_FRAME_IN_PCAP_FILE
                        The last frame in each PCAP file is often corrupted. This flag makes the pcap reader skip the
                        last frame in each file.
  --raise-on-error RAISE_ON_ERROR
                        The frame processing will raise an exception if the distance between the actual and the
                        estimated position is larger than this number. Set to 0 or lower to deactivate.
  --raise-on-movement RAISE_ON_MOVEMENT
                        The frame processing will raise an exception if the distance between two last estimated
                        positions is larger than this number. Set to 0 or lower to deactivate.
  --wait-after-initial-frame WAIT_AFTER_INITIAL_FRAME
                        If given, the analysis will wait for this many seconds after the first frame to allow the
                        visualization to be manually adjusted (zooming, panning, etc).
```

## Absolute (point cloud) navigation
absoluteNavigator.py runs through all frames the given PCAP file, and uses the selected registration algorithm to register each frame against the full point cloud (technically it extracts a small part of the point cloud around the current position, and registers against that, since registering against the full cloud didn't work). The input arguments for the absolute navigation is very similar to the incremental navigation arguments, so see above for some more explanation and examples.

The main difference is the --point-cloud argument, which gives the location of the full point cloud to navigate against (created using pointCloud.py, see above).

**Full argument description:**
```
usage: absoluteNavigator.py [-h] --pcap PCAP [PCAP ...] [--json JSON [JSON ...]] [--sbet SBET]
                            [--sbet-z-offset SBET_Z_OFFSET] [--recreate-caches] --point-cloud POINT_CLOUD
                            [--algorithm ALGORITHM] [--frames FRAMES] [--build-cloud-after BUILD_CLOUD_AFTER]
                            [--skip-every-frame SKIP_EVERY_FRAME] [--skip-until-radius SKIP_UNTIL_RADIUS]
                            [--skip-until-x SKIP_UNTIL_X] [--skip-until-y SKIP_UNTIL_Y] [--skip-start SKIP_START]
                            [--voxel-size VOXEL_SIZE] [--downsample-after DOWNSAMPLE_AFTER]
                            [--preview {always,end,never}] [--save-to SAVE_TO]
                            [--save-screenshots-to SAVE_SCREENSHOTS_TO] [--save-frame-pairs-to SAVE_FRAME_PAIRS_TO]
                            [--save-frame-pair-threshold SAVE_FRAME_PAIR_THRESHOLD]
                            [--skip-last-frame-in-pcap-file SKIP_LAST_FRAME_IN_PCAP_FILE]
                            [--raise-on-error RAISE_ON_ERROR] [--raise-on-movement RAISE_ON_MOVEMENT]
                            [--wait-after-initial-frame WAIT_AFTER_INITIAL_FRAME]

options:
  -h, --help            show this help message and exit
  --pcap PCAP [PCAP ...]
                        The path to one or more PCAP files to visualize, relative or absolute. A path to a directory
                        containing multiple pcap files can also be provided.
  --json JSON [JSON ...]
                        The path to corresponding JSON file(s) for each of the PCAP file(s) with the sensor metadata,
                        relative or absolute. If this is not given, the PCAP location is used (by replacing .pcap with
                        .json). A path to a directory containing multiple json files can also be provided.
  --sbet SBET           The path to a corresponding SBET file with GNSS coordinates.
  --sbet-z-offset SBET_Z_OFFSET
                        If the GNSS positions in the SBET file have an altitude offset from the point cloud, this
                        argument will be added/subtracted on the Z coordinates of each SBET coordinate.
  --recreate-caches
  --point-cloud POINT_CLOUD
                        An Open3D point cloud file to use for absolute navigation.
  --algorithm ALGORITHM
                        Use this registration algorithm (see names in algorithmHelper.py).
  --frames FRAMES       If given a number larger than 1, only this many frames will be read from the PCAP file.
  --build-cloud-after BUILD_CLOUD_AFTER
                        How often registered frames should be added to the generated point cloud. 0 or lower
                        deactivates the generated point cloud. 1 or higher generates a point cloud with details (and
                        time usage) decreasing with higher numbers.
  --skip-every-frame SKIP_EVERY_FRAME
                        If given a positive number larger than 0, this many frames will be skipped between every frame
                        read from the PCAP file.
  --skip-until-radius SKIP_UNTIL_RADIUS
                        If given together with --skip-until-x and --skip-until-y, the analysis will skip frames until
                        the actual position enters the circle given by these three parameters.
  --skip-until-x SKIP_UNTIL_X
                        If given together with --skip-until-x and --skip-until-radius, the analysis will skip frames
                        until the actual position enters the circle given by these three parameters.
  --skip-until-y SKIP_UNTIL_Y
                        If given together with --skip-until-y and --skip-until-radius, the analysis will skip frames
                        until the actual position enters the circle given by these three parameters.
  --skip-start SKIP_START
                        If given a positive number larger than 0, this many frames will be skipped before starting
                        processing frames.
  --voxel-size VOXEL_SIZE
                        The voxel size used for cloud downsampling. If less than or equal to zero, downsampling will
                        be disabled.
  --downsample-after DOWNSAMPLE_AFTER
                        The cloud will be downsampled (which is an expensive operation for large clouds, so don't do
                        it too often) after this many registered frames have been added. If this number is higher than
                        the number of frames being read, it will be downsampled once at the end of the process (unless
                        downsampling is disabled, see --voxel-size).
  --preview {always,end,never}
                        Show constantly updated point cloud and data plot previews while processing ('always'), show
                        them only at the end ('end'), or don't show them at all ('never').
  --save-to SAVE_TO     If given, final results will be stored in this folder.
  --save-screenshots-to SAVE_SCREENSHOTS_TO
                        If given, point cloud screenshots will be saved in this directory with their indices as
                        filenames (0.png, 1.png, 2.png, etc). Only works if --preview is set to 'always'.
  --save-frame-pairs-to SAVE_FRAME_PAIRS_TO
                        If given, frame pairs with a registered fitness below --save-frame-pair-threshold will be
                        saved to the given directory for manual inspection.
  --save-frame-pair-threshold SAVE_FRAME_PAIR_THRESHOLD
                        If --save-frame-pairs-to is given, frame pairs with a registered fitness value below this
                        value will be saved.
  --skip-last-frame-in-pcap-file SKIP_LAST_FRAME_IN_PCAP_FILE
                        The last frame in each PCAP file is often corrupted. This flag makes the pcap reader skip the
                        last frame in each file.
  --raise-on-error RAISE_ON_ERROR
                        The frame processing will raise an exception if the distance between the actual and the
                        estimated position is larger than this number. Set to 0 or lower to deactivate.
  --raise-on-movement RAISE_ON_MOVEMENT
                        The frame processing will raise an exception if the distance between two last estimated
                        positions is larger than this number. Set to 0 or lower to deactivate.
  --wait-after-initial-frame WAIT_AFTER_INITIAL_FRAME
                        If given, the analysis will wait for this many seconds after the first frame to allow the
                        visualization to be manually adjusted (zooming, panning, etc).
```
