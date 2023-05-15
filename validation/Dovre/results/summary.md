<a name="pointclouds"></a>
# Point clouds
The point clouds are generated from trip 3 in 2021 and trip 1 in 2022 by the NMA. The resulting .laz files are merged into one using the following commands:
```
python pointCloud.py --create-from "validation\Dovre\2021-10-20\pointcloud" --preview never --write-to "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --voxel-size 0.1
python pointCloud.py --create-from "validation\Dovre\2022-01-26\pointcloud" --preview never --write-to "validation\Dovre\2022-01-26\pointcloud\combined_100.pcd" --voxel-size 0.1
```

<a name="details"></a>
## Details

This section is about Dovre specifically. See [this document](./../../_notes/summary.md) for more method details that are common for all four locations.

To make the results comparable, the trip analyses all started at the same point. This point is indicated with the white circle on the image above. The analyses ran until failure, or until the actual position reached the end circle (black).

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

<a name="abs-pcap2021-pc2021"></a>
### Absolute, PCAPs from 2021, point cloud from 2021

```
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\1_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\1_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\1_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\1_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\2_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\2_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\2_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\2_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\3_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\3_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\3_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\3_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\4_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\4_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\4_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\4_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\5_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\5_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\5_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\5_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
```

<a name="abs-pcap2022-pc2021"></a>
### Absolute, PCAPs from 2022, point cloud from 2021

```
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\1_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\1_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\1_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\1_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\2_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\2_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\2_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\2_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\3_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\3_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\3_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\3_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\4_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\4_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\4_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\4_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\5_ned_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\5_ned_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
python absoluteNavigator.py --pcap "validation\Dovre\2021-10-20\pcap\5_opp_20hz" --sbet "validation\Dovre\2021-10-20\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Dovre\2021-10-20\pointcloud\combined_100.pcd" --save-to "validation\Dovre\results\ABS, PCAP2021, PC2021\5_opp_20hzhz" --load-arguments "validation\Dovre\default-arguments.json"
```