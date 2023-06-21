#### Table of Contents
* [Drivdalen](#header)
  * [The collected datasets](#datasets)
    * [October 22th 2021 (without snow)](#2021)
    * [February 16th 2022 (with snow)](#2022)
  * [Point clouds](#pointclouds)
* [The analysis](#analysis)
  * [Details](#details)
  * [Absolute navigation](#analysis-abs)
  * [Incremental navigation](#analysis-inc)
* [Run configs](#run-configs)
  * [Absolute, PCAPs from 2021, point cloud from 2021](#abs-pcap2021-pc2021)
  * [Absolute, PCAPs from 2021, point cloud from 2022](#abs-pcap2021-pc2022)
  * [Absolute, PCAPs from 2022, point cloud from 2021](#abs-pcap2022-pc2021)
  * [Absolute, PCAPs from 2022, point cloud from 2022](#abs-pcap2022-pc2022)
  * [Incremental, PCAPs from 2021](#inc-pcap2021)
  * [Incremental, PCAPs from 2022](#inc-pcap2022)

<a name="header"></a>
# Lismarka

<a name="datasets"></a>
## The collected datasets

<a name="2021"></a>
### October 22th 2021 (without snow):
| Trip# | Direction | Frequency | Start time | Comment |
|-------|-----------|-----------|------------|---------|
| 1     | West-East | 10 hz     | 10:48      | OK      |
| 2     | East-West | 10 hz     | 10:57      | OK      |
| 3     | West-East | 10 hz     | 11:04      | OK      |
| 4     | East-West | 10 hz     | 11:11      | OK      |
| 5     | West-East | 20 hz     | 11:19      | OK      |
| 6     | East-West | 20 hz     | 11:28      | OK      |
| 7     | West-East | 20 hz     | 11:35      | OK      |
| 8     | East-West | 20 hz     | 11:45      | OK      |
| 9     | West-East | 20 hz     | 11:53      | OK      |
| 10    | East-West | 20 hz     | 12:00      | OK      |


<a name="2022"></a>
### February 16th 2022 (with snow):
| Trip# | Direction | Frequency | Start time | Comment |
|-------|-----------|-----------|------------|---------|
| 1     | West-East | 10 hz     | 17:36      | OK      |
| 2     | East-West | 10 hz     | 17:51      | OK      |
| 3     | West-East | 10 hz     | 17:57      | OK      |
| 4     | East-West | 10 hz     | 18:03      | OK      |
| 5     | East-West | 20 hz     | 18:13      | OK      |
| 6     | West-East | 20 hz     | 18:18      | OK      |
| 7     | East-West | 20 hz     | 18:24      | OK      |
| 8     | West-East | 20 hz     | 18:30      | OK      |
| 9     | East-West | 20 hz     | 18:35      | OK      |
| 10    | West-East | 20 hz     | 18:41      | OK      |

The trips are recorded in both directions; the two white circles show the analysis start or end points depending on which direction the trip is. 

![The driving route shown on a map.](full_route.png)

<a name="pointclouds"></a>
# Point clouds
The point clouds are generated from trip 1 in 2021 and trip 1 in 2022 by the NMA. The resulting .laz files are merged into one using the following commands:
```
python pointCloud.py --create-from "validation\Lismarka\2021-10-22\pointcloud" --write-to "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --voxel-size 0.1
python pointCloud.py --create-from "validation\Lismarka\2022-02-16\pointcloud" --write-to "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --voxel-size 0.1
```

<a name="analysis"></a>
# The analysis

<a name="details"></a>
## Details

This section is about Lismarka specifically. See [this document](./../../_notes/summary.md) for more method details that are common for all four locations.

To make the results comparable, the trip analyses all started at the same point. This point is indicated with the white circle on the image above. The analyses ran until failure, or until the actual position reached the end circle.

**Common command line arguments:**

Differs by trip direction. Command line arguments are identical except for switched skip-until and run-until arguments.

West-East:
```
{
    "preview": "always",
    "build-cloud-after": 5,
    "skip-until-x": 581089.271,
    "skip-until-y": 6773020.305,
    "run-until-x": 583937.3003,
    "run-until-y": 6771878.0647,
    "recreate-caches": true,
    "max-frame-radius": 25,
    "wait-after-first-frame": 15,
    "hide-point-cloud": true,
    "save-after-first-frame": true,
    "save-after-frames": 50,
    "raise-on-2d-error": 25,
    "raise-on-3d-error": 50,
    "sbet-crs-from": 4937,
    "sbet-crs-to": 5972,
    "use-actual-coordinate": false,
    "voxel-size": 0.1
}
```

East-West:
```
{
    "preview": "always",
    "build-cloud-after": 5,
    "skip-until-x": 583937.3003,
    "skip-until-y": 6771878.0647,
    "run-until-x": 581089.271,
    "run-until-y": 6773020.305,
    "recreate-caches": true,
    "max-frame-radius": 25,
    "wait-after-first-frame": 15,
    "hide-point-cloud": true,
    "save-after-first-frame": true,
    "save-after-frames": 50,
    "raise-on-2d-error": 25,
    "raise-on-3d-error": 50,
    "sbet-crs-from": 4937,
    "sbet-crs-to": 5972,
    "use-actual-coordinate": false,
    "voxel-size": 0.1
}
```

<a name="analysis-abs"></a>
## Absolute navigation

_**Meters driven before failure**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | 289.322 | 73.052 | 0.794 | 3,117.627 |
| 2     | 3,674.835 | 336.565 | 6.677 | 3,674.865 |
| 3     | 1.873 | 63.328 | 0.864 | 2,992.915 |
| 4     | 205.599 | 347.554 | 122.256 | 3,675.426 |
| 5     | 3,552.647 | 268.591 | 0.462 | 3,675.999 |
| 6     | 689.312 | 335.172 | 3.415 | 3,678.367 |
| 7     | 2,878.482 | 263.067 | 0.389 | 3,115.435 |
| 8     | 148.814 | 332.559 | 3.299 | 3,678.642 |
| 9     | N/P | N/P | 0.936 | 23.200 |
| 10     | 157.756 | 342.979 | 3.276 | 3,677.890 |
| **Average** | **1,288.738** | **262.541** | **14.237** | **3,131.037** |



_**Percentage of route driven before failure**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | 7.7 | 1.9 | 0.0 | 83.1 |
| 2     | 98.0 | 9.0 | 0.2 | 98.0 |
| 3     | 0.0 | 1.7 | 0.0 | 79.8 |
| 4     | 5.5 | 9.3 | 3.3 | 98.0 |
| 5     | 94.7 | 7.2 | 0.0 | 98.0 |
| 6     | 18.4 | 8.9 | 0.1 | 98.1 |
| 7     | 76.8 | 7.0 | 0.0 | 83.1 |
| 8     | 4.0 | 8.9 | 0.1 | 98.1 |
| 9     | N/P | N/P | 0.0 | 0.6 |
| 10     | 4.2 | 9.1 | 0.1 | 98.1 |
| **Average** | **34.4** | **7.0** | **0.4** | **83.5** |



_**2D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | 0.774 | 8.809 | 10.496 | 4.362 |
| 2     | 0.955 | 1.150 | 10.149 | 1.168 |
| 3     | 8.188 | 8.426 | 10.425 | 4.615 |
| 4     | 4.072 | 2.063 | 2.656 | 0.979 |
| 5     | 0.887 | 2.385 | 9.253 | 3.999 |
| 6     | 0.793 | 1.284 | 11.183 | 0.718 |
| 7     | 0.852 | 2.362 | 8.588 | 3.937 |
| 8     | 0.788 | 1.608 | 6.953 | 0.705 |
| 9     | N/P | N/P | 14.419 | 2.338 |
| 10     | 0.524 | 2.105 | 9.042 | 0.708 |
| **Average** | **1.981** | **3.355** | **9.316** | **2.353** |



_**3D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | 0.954 | 8.847 | 10.530 | 4.392 |
| 2     | 1.096 | 1.268 | 10.273 | 1.356 |
| 3     | 8.206 | 8.449 | 10.436 | 4.642 |
| 4     | 4.289 | 2.160 | 2.912 | 1.179 |
| 5     | 1.025 | 2.398 | 9.258 | 4.036 |
| 6     | 0.999 | 1.371 | 11.286 | 0.940 |
| 7     | 0.986 | 2.375 | 8.608 | 3.971 |
| 8     | 1.044 | 1.702 | 7.116 | 0.925 |
| 9     | N/P | N/P | 14.473 | 2.348 |
| 10     | 0.862 | 2.161 | 9.158 | 0.930 |
| **Average** | **2.162** | **3.415** | **9.405** | **2.472** |



_**Reported registration fitness**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | 0.882 | 0.820 | 0.803 | 0.996 |
| 2     | 0.924 | 0.967 | 0.907 | 1.000 |
| 3     | 0.821 | 0.866 | 0.840 | 0.996 |
| 4     | 0.907 | 0.957 | 0.953 | 0.999 |
| 5     | 0.925 | 0.979 | 0.843 | 0.996 |
| 6     | 0.933 | 0.963 | 0.879 | 1.000 |
| 7     | 0.924 | 0.983 | 0.809 | 0.996 |
| 8     | 0.939 | 0.961 | 0.889 | 1.000 |
| 9     | N/P | N/P | 0.753 | 0.989 |
| 10     | 0.940 | 0.960 | 0.882 | 0.999 |
| **Average** | **0.910** | **0.940** | **0.856** | **0.997** |



_**Reported registration RMSE**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | 0.180 | 0.337 | 0.392 | 0.131 |
| 2     | 0.139 | 0.282 | 0.330 | 0.092 |
| 3     | 0.324 | 0.320 | 0.402 | 0.134 |
| 4     | 0.185 | 0.291 | 0.241 | 0.098 |
| 5     | 0.135 | 0.249 | 0.382 | 0.124 |
| 6     | 0.138 | 0.276 | 0.325 | 0.084 |
| 7     | 0.131 | 0.242 | 0.393 | 0.126 |
| 8     | 0.126 | 0.280 | 0.308 | 0.084 |
| 9     | N/P | N/P | 0.422 | 0.104 |
| 10     | 0.121 | 0.279 | 0.313 | 0.086 |
| **Average** | **0.164** | **0.284** | **0.351** | **0.106** |



_**Registration iterations before convergence**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | 118.665 | 199.242 | 250.000 | 70.526 |
| 2     | 127.524 | 145.961 | 225.000 | 58.039 |
| 3     | 250.000 | 201.724 | 225.000 | 71.516 |
| 4     | 145.470 | 149.508 | 144.355 | 59.711 |
| 5     | 106.087 | 94.855 | 250.000 | 60.357 |
| 6     | 114.787 | 143.926 | 225.000 | 47.217 |
| 7     | 105.249 | 95.954 | 175.000 | 61.511 |
| 8     | 112.832 | 144.415 | 225.000 | 47.136 |
| 9     | N/P | N/P | 225.000 | 98.980 |
| 10     | 111.983 | 138.927 | 250.000 | 47.910 |
| **Average** | **132.511** | **146.057** | **219.435** | **62.290** |



_**LiDAR Frequency**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | 10 hz | 10 hz | 10 hz | 10 hz |
| 2     | 10 hz | 10 hz | 10 hz | 10 hz |
| 3     | 10 hz | 10 hz | 10 hz | 10 hz |
| 4     | 10 hz | 10 hz | 10 hz | 10 hz |
| 5     | 20 hz | 20 hz | 20 hz | 20 hz |
| 6     | 20 hz | 20 hz | 20 hz | 20 hz |
| 7     | 20 hz | 20 hz | 20 hz | 20 hz |
| 8     | 20 hz | 20 hz | 20 hz | 20 hz |
| 9     | 20 hz | 20 hz | 20 hz | 20 hz |
| 10     | 20 hz | 20 hz | 20 hz | 20 hz |



_**Links to individual trip details**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/1_ost_10hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/1_ost_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/1_ost_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/1_ost_10hz) |
| 2     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/1_vest_10hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/1_vest_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/1_vest_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/1_vest_10hz) |
| 3     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/2_ost_10hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/2_ost_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/2_ost_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/2_ost_10hz) |
| 4     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/2_vest_10hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/2_vest_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/2_vest_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/2_vest_10hz) |
| 5     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/3_ost_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/3_ost_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/3_ost_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/3_ost_20hz) |
| 6     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/3_vest_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/3_vest_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/3_vest_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/3_vest_20hz) |
| 7     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/4_ost_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/4_ost_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/4_ost_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/4_ost_20hz) |
| 8     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/4_vest_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/4_vest_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/4_vest_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/4_vest_20hz) |
| 9     | N/P | N/P | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/5_ost_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/5_ost_20hz) |
| 10     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/5_vest_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/5_vest_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/5_vest_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/5_vest_20hz) |

<a name="abs-pcap2021-pc2021"></a>
### Absolute, PCAPs from 2021, point cloud from 2021

```
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\1_ost_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\1_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\1_vest_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\1_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\2_ost_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\2_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\2_vest_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\2_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\3_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\3_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\3_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\3_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\4_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\4_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\4_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\4_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\5_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\5_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\5_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2021\5_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
```

<a name="abs-pcap2021-pc2022"></a>
### Absolute, PCAPs from 2021, point cloud from 2022

```
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\1_ost_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\1_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\1_vest_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\1_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\2_ost_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\2_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\2_vest_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\2_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\3_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\3_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\3_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\3_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\4_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\4_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\4_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\4_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\5_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\5_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\5_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2021, PC2022\5_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
```

<a name="abs-pcap2022-pc2021"></a>
### Absolute, PCAPs from 2022, point cloud from 2021

```
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\1_ost_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\1_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\1_vest_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\1_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\2_ost_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\2_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\2_vest_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\2_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\3_ost_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\3_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\3_vest_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\3_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\4_ost_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\4_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\4_vest_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\4_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\5_ost_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\5_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\5_vest_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2021-10-22\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2021\5_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
```

<a name="abs-pcap2022-pc2022"></a>
### Absolute, PCAPs from 2022, point cloud from 2022

```
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\1_ost_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\1_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\1_vest_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\1_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\2_ost_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\2_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\2_vest_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\2_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\3_ost_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\3_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\3_vest_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\3_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\4_ost_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\4_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\4_vest_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\4_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\5_ost_20Hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\5_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python absoluteNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\5_vest_20Hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --point-cloud "validation\Lismarka\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lismarka\results\ABS, PCAP2022, PC2022\5_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
```


<a name="inc-pcap2021"></a>
### Incremental, PCAPs from 2021

```
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\1_ost_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\1_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\1_vest_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\1_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\2_ost_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\2_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\2_vest_10hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\2_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\3_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\3_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\3_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\3_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\4_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\4_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\4_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\4_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\5_ost_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\5_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2021-10-22\pcap\5_vest_20hz" --sbet "validation\Lismarka\2021-10-22\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lismarka\results\INC, PCAP2021\5_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
```

<a name="inc-pcap2022"></a>
### Incremental, PCAPs from 2022

```
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\1_ost_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\1_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\1_vest_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\1_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\2_ost_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\2_ost_10hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\2_vest_10hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\2_vest_10hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\3_ost_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\3_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\3_vest_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\3_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\4_ost_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\4_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\4_vest_20hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\4_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\5_ost_20Hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\5_ost_20hz" --load-arguments "validation\Lismarka\default-arguments.json" --preview never
python incrementalNavigator.py --pcap "validation\Lismarka\2022-02-16\pcap\5_vest_20Hz" --sbet "validation\Lismarka\2022-02-16\navigation\sbet-output.out" --save-to "validation\Lismarka\results\INC, PCAP2022\5_vest_20hz" --load-arguments "validation\Lismarka\default-arguments-reversed.json" --preview never
```