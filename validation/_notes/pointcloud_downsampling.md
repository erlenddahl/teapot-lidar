# Point cloud downsampling tests

These notes document tests made to decide how much the full point cloud can be downsampled without affecting accuracy more than what is acceptable.

Created a lot of point clouds:
```
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_001.pcd" --voxel-size 0.001
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_005.pcd" --voxel-size 0.005
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_010.pcd" --voxel-size 0.010
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_025.pcd" --voxel-size 0.025
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_040.pcd" --voxel-size 0.040
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_050.pcd" --voxel-size 0.050
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_075.pcd" --voxel-size 0.075
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --voxel-size 0.100
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_125.pcd" --voxel-size 0.125
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_150.pcd" --voxel-size 0.150
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_200.pcd" --voxel-size 0.200
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_300.pcd" --voxel-size 0.300
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_400.pcd" --voxel-size 0.400
python pointCloud.py --create-from "validation\Lillehammer\2021-10-21\pointcloud\Referansepunktsky" --preview never --write-to "validation\Lillehammer\2021-10-21\pointcloud\combined_500.pcd" --voxel-size 0.500
```

Then ran a short sequence (70 frames of a pcap file in the middle of a sharp turn) on each of them.
```
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_001.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\001" --visualization-window-name 001 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_005.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\005" --visualization-window-name 005 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_010.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\010" --visualization-window-name 010 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_025.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\025" --visualization-window-name 025 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_040.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\040" --visualization-window-name 040 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_050.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\050" --visualization-window-name 050 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_075.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\075" --visualization-window-name 075 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_100.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\100" --visualization-window-name 100 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_125.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\125" --visualization-window-name 125 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_150.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\150" --visualization-window-name 150 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_200.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\200" --visualization-window-name 200 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_300.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\300" --visualization-window-name 300 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_400.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\400" --visualization-window-name 400 --preview never
python absoluteNavigator.py --pcap "validation\Lillehammer\2021-10-21\pcap\3_10hz\OS-1-128_992035000186_1024x10_20211021_194805.pcap" --sbet "validation\Lillehammer\2021-10-21\navigation\sbet-output-UTC-1000.out" --point-cloud "validation\Lillehammer\2021-10-21\pointcloud\combined_500.pcd" --frames 70 --save-to "validation\testing\pointcloud_downsampling\500" --visualization-window-name 500 --preview never
```

Results show that the error and time usage is mostly the same until 0.050, which is reasonable as the original point cloud was created with a voxel size of 0.050. Note that the number of points in the point cloud changes before 0.050 is reached, probably due to how the downsampling algorithm works, and possibly due to differences in the downsampling used when creating the point cloud and here.

A good balance between accuracy and time usage is found at 0.100 or 0.125. Note that the average errors shouldn't be trusted, because the nasty rotation skewing problem wasn't solved at the time of this test.

| Voxel size | Points      | Time usage registration | Avg 2D Error | Avg 3D Error | Visual inspection         |
|------------|-------------|-------------------------|--------------|--------------|---------------------------|
| 0.001      | 224 225 299 | 1292                    | 0.5399       | 0.5785       | Smooth                    |
| 0.005      | 224 207 666 | 1306                    | 0.5400       | 0.5785       | Smooth                    |
| 0.010      | 224 060 962 | 1290                    | 0.5399       | 0.5784       | Smooth                    |
| 0.025      | 220 184 326 | 1295                    | 0.5398       | 0.5784       | Smooth                    |
| 0.040      | 201 288 468 | 1181                    | 0.5397       | 0.5785       | Smooth                    |
| 0.050      | 174 044 378 |  995                    | 0.5387       | 0.5782       | Smooth                    |
| 0.075      | 102 682 076 |  677                    | 0.5341       | 0.5752       | Smooth                    |
| 0.100      |  61 836 233 |  526                    | 0.5282       | 0.5743       | Smooth                    |
| 0.125      |  40 008 715 |  359                    | 0.5198       | 0.5623       | Very slightly jagged      |
| 0.150      |  27 573 340 |  273                    | 0.5287       | 0.5690       | Slightly jagged           |
| 0.200      |  15 084 915 |  255                    | 0.4591       | 0.5029       | Quite jagged              |
| 0.300      |   6 294 191 |    -                    | -            | -            | Failed after 4 frames     |
| 0.400      |   3 349 017 |    -                    | -            | -            | Failed after 1 frame      |
| 0.500      |   2 049 732 |    -                    | -            | -            | Failed after 3 frames     |

A test on a full run (Lillehammer 2021, 3_10hz) for the most relevant values gave the following results:

| Voxel size | Time usage registration | Avg 2D Error | Avg 3D Error | Visual inspection         |
|------------|-------------------------|--------------|--------------|---------------------------|
| 0.100      | 22954                   | 0.5211       | 0.5878       | Almost smooth, some edges |
| 0.125      | 16689                   | 0.5929       | 0.6589       | Almost smooth, some edges |