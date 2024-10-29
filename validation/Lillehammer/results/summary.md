#### Table of Contents
* [Lillehammer](#header)
  * [The collected datasets](#datasets)
    * [October 21th 2021 (without snow)](#2021)
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
# Lillehammer

<a name="datasets"></a>
## The collected datasets

<a name="2021"></a>
### October 21th 2021 (without snow):
| Trip# | Frequency | Start time | Comment |
|-------|-----------|------------|---------|
| 1     | 10 hz     | 14:43      | No SBET data, unusable. Confirmed by KV. |
| 2     | 10 hz     | 15:09      | No SBET data, unusable. Confirmed by KV. |
| 3     | 10 hz     | 19:45      | OK |
| 4     | 10 hz     | 20:01      | OK |
| 5     | 20 hz     | 20:19      | OK |
| 6     | 20 hz     | 20:35      | OK, slight detour at 255855.01,6784094.03 |
| 7     | 20 hz     | 21:17      | OK |


<a name="2022"></a>
### February 16th 2022 (with snow):
| Trip# | Frequency | Start time | Comment |
|-------|-----------|------------|---------|
| 1     | 10 hz     | 19:53      | OK |
| 2     | 10 hz     | 20:04      | OK, navigation issues after 579295.42,6776465.81 |
| 3     | 20 hz     | 20:27      | OK, missing one PCAP file in the beginning, but we skip that part of the route in the analysis. |
| 4     | 20 hz     | 20:38      | OK |
| 5     | 20 hz     | 20:48      | OK |

The image below shows the driving route on a map of Lillehammer. All 10 valid trips are drawn, but as they are very similar, it's hard to differentiate them in this plot. The brown detour on the right hand side is part of the 2021 trips -- they started at the parking spot at the bottom end of the brown arm, and drove north before entering the standard route. The 2022 trips started approximately at the same spot, but drove west, directly entering the route. Because of this discrepancy, and because trip 2022-3 is missing a PCAP file, the analysis start point is set to be after all trips are driving the same route without issues (white circle), and because of the navigation issues in trip 2022-2, the end point is set to the last left turn (black circle).

![The driving route shown on a map.](full_route.png)

<a name="pointclouds"></a>
# Point clouds
The point clouds are generated from trip 3 in 2021 and trip 1 in 2022 by the NMA. The resulting .laz files are merged into one using the following commands:
```
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --voxel-size 0.1
python pointCloud.py --create-from "validation\Lillehammer\2022-02-16\pointcloud" --preview never --write-to "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --voxel-size 0.1
```

<a name="analysis"></a>
# The analysis

<a name="details"></a>
## Details

This section is about Lillehammer specifically. See [this document](./../../_notes/summary.md) for more method details that are common for all four locations.

To make the results comparable, the trip analyses all started at the same point, which is set to after the missing PCAP file of trip 3 in 2022. This point is indicated with the white circle on the image above. The analyses ran until failure, or until the actual position reached the end circle (black).

**Common command line arguments:**
```
{
    "preview": "always",
    "build-cloud-after": 5,
    "skip-until-x": 579490.13,
    "skip-until-y": 6776060.22,
    "run-until-x": 579295.42,
    "run-until-y": 6776465.81,
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

The absolute navigation tables show how well the navigation worked in each of the four weather situations:
 - Bare/Bare means that the trips from 2021 (without snow) are run against the point cloud from 2021 (without snow).
 - Bare/Snow means that the trips from 2021 (without snow) are run against the point cloud from 2022 (with snow).
 - Snow/Bare means that the trips from 2022 (with snow) are run against the point cloud from 2021 (without snow).
 - Snow/Snow means that the trips from 2022 (with snow) are run against the point cloud from 2022 (with snow).

The numbers in the four results column represents the results for that combination, and are explained before each of the tables. Letters in those columns mean:
- N/A: This trip does not exist in this source material.
- N/P: This trip has not yet been processed.

_**Meters driven before failure**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 3,210.851 | 3,201.010 |
| 2     | N/A | N/A | 50.340 | 3,209.959 |
| 3     | 3,206.431 | 3,206.431 | 3,216.194 | 3,181.106 |
| 4     | 3,205.241 | 3,205.241 | 63.694 | 3,206.707 |
| 5     | 3,206.739 | 3,206.737 | 3,210.271 | 3,210.267 |
| 6     | 3,207.228 | 3,207.167 | N/A | N/A |
| 7     | 3,209.495 | 3,210.130 | N/A | N/A |
| **Average** | **3,207.027** | **3,207.141** | **1,950.270** | **3,201.810** |



_**Percentage of route driven before failure**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 100.0 | 100.0 |
| 2     | N/A | N/A | 1.6 | 100.0 |
| 3     | 100.0 | 100.0 | 100.0 | 99.4 |
| 4     | 100.0 | 100.0 | 2.0 | 100.0 |
| 5     | 100.0 | 100.0 | 100.0 | 100.0 |
| 6     | 100.0 | 100.0 | N/A | N/A |
| 7     | 100.0 | 100.0 | N/A | N/A |
| **Average** | **100.0** | **100.0** | **60.7** | **99.9** |



_**2D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.781 | 0.789 |
| 2     | N/A | N/A | 5.880 | 0.828 |
| 3     | 0.576 | 1.051 | 0.851 | 0.871 |
| 4     | 0.592 | 1.052 | 2.710 | 0.912 |
| 5     | 0.538 | 1.020 | 0.869 | 0.889 |
| 6     | 0.536 | 0.980 | N/A | N/A |
| 7     | 0.535 | 1.017 | N/A | N/A |
| **Average** | **0.555** | **1.024** | **2.218** | **0.858** |



_**3D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.897 | 0.942 |
| 2     | N/A | N/A | 6.082 | 0.963 |
| 3     | 0.649 | 1.178 | 0.949 | 1.013 |
| 4     | 0.677 | 1.180 | 2.769 | 1.036 |
| 5     | 0.622 | 1.153 | 0.974 | 1.030 |
| 6     | 0.632 | 1.119 | N/A | N/A |
| 7     | 0.624 | 1.152 | N/A | N/A |
| **Average** | **0.641** | **1.157** | **2.334** | **0.997** |



_**Reported registration fitness**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.980 | 0.999 |
| 2     | N/A | N/A | 0.828 | 1.000 |
| 3     | 0.985 | 0.996 | 0.983 | 1.000 |
| 4     | 0.983 | 0.995 | 0.968 | 1.000 |
| 5     | 0.986 | 0.997 | 0.983 | 1.000 |
| 6     | 0.984 | 0.996 | N/A | N/A |
| 7     | 0.985 | 0.994 | N/A | N/A |
| **Average** | **0.985** | **0.996** | **0.948** | **1.000** |



_**Reported registration RMSE**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.156 | 0.085 |
| 2     | N/A | N/A | 0.253 | 0.069 |
| 3     | 0.097 | 0.151 | 0.146 | 0.069 |
| 4     | 0.111 | 0.154 | 0.202 | 0.076 |
| 5     | 0.103 | 0.143 | 0.146 | 0.070 |
| 6     | 0.105 | 0.148 | N/A | N/A |
| 7     | 0.103 | 0.144 | N/A | N/A |
| **Average** | **0.104** | **0.148** | **0.180** | **0.074** |



_**Registration iterations before convergence**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 86.867 | 56.924 |
| 2     | N/A | N/A | 145.312 | 51.809 |
| 3     | 80.763 | 65.075 | 85.151 | 48.620 |
| 4     | 81.965 | 66.860 | 108.028 | 51.048 |
| 5     | 79.683 | 57.975 | 81.338 | 49.417 |
| 6     | 77.544 | 58.624 | N/A | N/A |
| 7     | 80.368 | 59.338 | N/A | N/A |
| **Average** | **80.064** | **61.574** | **101.339** | **51.564** |



_**LiDAR Frequency**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | - | - | 10 hz | 10 hz |
| 2     | - | - | 10 hz | 10 hz |
| 3     | 10 hz | 10 hz | 20 hz | 20 hz |
| 4     | 10 hz | 10 hz | 20 hz | 20 hz |
| 5     | 20 hz | 20 hz | 20 hz | 20 hz |
| 6     | 20 hz | 20 hz | - | - |
| 7     | 20 hz | 20 hz | - | - |



_**Links to individual trip details**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/1_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/1_10hz) |
| 2     | N/A | N/A | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/2_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/2_10hz) |
| 3     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/3_10hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/3_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/3_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/3_20hz) |
| 4     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/4_10hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/4_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/4_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/4_20hz) |
| 5     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/5_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/5_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/5_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/5_20hz) |
| 6     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/6_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/6_20hz) | N/A | N/A |
| 7     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/7_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/7_20hz) | N/A | N/A |

<a name="analysis-inc"></a>
## Incremental navigation

_**Meters driven before failure**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | 549.095 |
| 2     | N/A | 33.903 |
| 3     | 39.635 | 1,162.963 |
| 4     | 119.949 | 1,125.724 |
| 5     | 17.273 | 734.214 |
| 6     | 170.684 | N/A |
| 7     | 169.580 | N/A |
| **Average** | **103.424** | **721.180** |



_**Percentage of route driven before failure**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | 17.2 |
| 2     | N/A | 1.1 |
| 3     | 1.2 | 36.3 |
| 4     | 3.7 | 35.2 |
| 5     | 0.5 | 22.9 |
| 6     | 5.3 | N/A |
| 7     | 5.3 | N/A |
| **Average** | **3.2** | **22.5** |



_**2D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | 5.846 |
| 2     | N/A | 0.709 |
| 3     | 1.678 | 12.920 |
| 4     | 1.736 | 14.035 |
| 5     | 3.960 | 5.322 |
| 6     | 1.989 | N/A |
| 7     | 1.926 | N/A |
| **Average** | **2.258** | **7.766** |



_**3D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | 11.038 |
| 2     | N/A | 0.733 |
| 3     | 1.688 | 28.956 |
| 4     | 2.253 | 28.611 |
| 5     | 3.975 | 14.466 |
| 6     | 3.809 | N/A |
| 7     | 3.633 | N/A |
| **Average** | **3.071** | **16.761** |



_**Reported registration fitness**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | 0.999 |
| 2     | N/A | 1.000 |
| 3     | 0.987 | 1.000 |
| 4     | 0.995 | 1.000 |
| 5     | 0.953 | 0.999 |
| 6     | 0.999 | N/A |
| 7     | 0.999 | N/A |
| **Average** | **0.987** | **0.999** |



_**Reported registration RMSE**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | 0.126 |
| 2     | N/A | 0.138 |
| 3     | 0.174 | 0.090 |
| 4     | 0.167 | 0.090 |
| 5     | 0.228 | 0.094 |
| 6     | 0.137 | N/A |
| 7     | 0.136 | N/A |
| **Average** | **0.168** | **0.108** |



_**Registration iterations before convergence**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | 47.240 |
| 2     | N/A | 38.208 |
| 3     | 56.000 | 40.294 |
| 4     | 44.715 | 39.399 |
| 5     | 85.714 | 41.802 |
| 6     | 38.078 | N/A |
| 7     | 35.269 | N/A |
| **Average** | **51.955** | **41.388** |



_**Time usage per frame**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | 5.846 |
| 2     | N/A | 0.709 |
| 3     | 1.678 | 12.920 |
| 4     | 1.736 | 14.035 |
| 5     | 3.960 | 5.322 |
| 6     | 1.989 | N/A |
| 7     | 1.926 | N/A |
| **Average** | **2.258** | **7.766** |



_**Processing status**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/P | failed |
| 2     | N/P | failed |
| 3     | failed | failed |
| 4     | failed | failed |
| 5     | failed | failed |
| 6     | failed | N/P |
| 7     | failed | N/P |



_**Ended because**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/P | The navigation error (38.02514395423351) is larger than the given limit (--raise-on-2d-error 25). |
| 2     | N/P | The navigation error (29.556631867084317) is larger than the given limit (--raise-on-2d-error 25). |
| 3     | The navigation error (26.46795609797709) is larger than the given limit (--raise-on-2d-error 25). | The navigation error (50.000193786462255) is larger than the given limit (--raise-on-3d-error 50). |
| 4     | The navigation error (32.42023327411043) is larger than the given limit (--raise-on-2d-error 25). | The navigation error (50.02988935361827) is larger than the given limit (--raise-on-3d-error 50). |
| 5     | The navigation error (37.68099111846967) is larger than the given limit (--raise-on-2d-error 25). | The navigation error (42.126285446961184) is larger than the given limit (--raise-on-2d-error 25). |
| 6     | The navigation error (34.50985922129513) is larger than the given limit (--raise-on-2d-error 25). | N/P |
| 7     | The navigation error (27.489356699540238) is larger than the given limit (--raise-on-2d-error 25). | N/P |



_**LiDAR Frequency**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | - | 10 hz |
| 2     | - | 10 hz |
| 3     | 10 hz | 20 hz |
| 4     | 10 hz | 20 hz |
| 5     | 20 hz | 20 hz |
| 6     | 20 hz | - |
| 7     | 20 hz | - |



_**Links to individual trip details**_
| Trip#   | Bare | Snow |
|---------|------|------|
| 1     | N/A | [Link](./INC%2C%20PCAP2022/1_10hz) |
| 2     | N/A | [Link](./INC%2C%20PCAP2022/2_10hz) |
| 3     | [Link](./INC%2C%20PCAP2021/3_10hz) | [Link](./INC%2C%20PCAP2022/3_20hz) |
| 4     | [Link](./INC%2C%20PCAP2021/4_10hz) | [Link](./INC%2C%20PCAP2022/4_20hz) |
| 5     | [Link](./INC%2C%20PCAP2021/5_20hz) | [Link](./INC%2C%20PCAP2022/5_20hz) |
| 6     | [Link](./INC%2C%20PCAP2021/6_20hz) | N/A |
| 7     | [Link](./INC%2C%20PCAP2021/7_20hz) | N/A |

<a name="run-configs"></a>
## Run configurations

<a name="abs-pcap2021-pc2021"></a>
### Absolute, PCAPs from 2021, point cloud from 2021

```
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2021\3_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\4_10hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2021\4_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\5_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2021\5_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\6_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2021\6_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\7_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2021\7_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
```

<a name="abs-pcap2021-pc2022"></a>
### Absolute, PCAPs from 2021, point cloud from 2022

```
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2022\3_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\4_10hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2022\4_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\5_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2022\5_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\6_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2022\6_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\7_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2021, PC2022\7_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
```

<a name="abs-pcap2022-pc2021"></a>
### Absolute, PCAPs from 2022, point cloud from 2021

```
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\1_10hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2021\1_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\2_10hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2021\2_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\3_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2021\3_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\4_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2021\4_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\5_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2021\5_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
```

<a name="abs-pcap2022-pc2022"></a>
### Absolute, PCAPs from 2022, point cloud from 2022

```
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\1_10hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2022\1_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\2_10hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2022\2_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\3_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2022\3_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\4_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2022\4_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\5_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --point-cloud "validation\Lillehammer\2022-02-16\pointcloud\combined_100.pcd" --save-to "validation\Lillehammer\results\ABS, PCAP2022, PC2022\5_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
```

<a name="inc-pcap2021"></a>
### Incremental, PCAPs from 2021

```
python incrementalNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\1_10hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lillehammer\results\INC, PCAP2021\1_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\2_10hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lillehammer\results\INC, PCAP2021\2_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lillehammer\results\INC, PCAP2021\3_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\4_10hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lillehammer\results\INC, PCAP2021\4_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\5_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lillehammer\results\INC, PCAP2021\5_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\6_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lillehammer\results\INC, PCAP2021\6_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\7_20hz" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --save-to "validation\Lillehammer\results\INC, PCAP2021\7_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
```

<a name="inc-pcap2022"></a>
### Incremental, PCAPs from 2022

```
python incrementalNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\1_10hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --save-to "validation\Lillehammer\results\INC, PCAP2022\1_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\2_10hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --save-to "validation\Lillehammer\results\INC, PCAP2022\2_10hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\3_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --save-to "validation\Lillehammer\results\INC, PCAP2022\3_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\4_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --save-to "validation\Lillehammer\results\INC, PCAP2022\4_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
python incrementalNavigator.py --pcap "validation\Lillehammer\2022-02-16\pcap\5_20hz" --sbet "validation\Lillehammer\2022-02-16\navigation\sbet_teapot.csv" --save-to "validation\Lillehammer\results\INC, PCAP2022\5_20hz" --load-arguments "validation\Lillehammer\default-arguments.json"
```
