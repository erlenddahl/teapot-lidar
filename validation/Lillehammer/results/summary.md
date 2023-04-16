# Lillehammer

## The collected datasets
![The driving route shown on a map.](full_route.png)

### October 21th 2021 (without snow):
| Trip# | Frequency | Start time | Comment |
|-------|-----------|------------|---------|
| 1     | 10 hz     | 14:43      | No SBET data, unusable. Confirmed by KV. |
| 2 | 10 hz | 15:09 | No SBET data, unusable. Confirmed by KV. |
| 3 | 10 hz | 19:45 | OK |
| 4 | 10 hz | 20:01 | OK |
| 5 | 20 hz | 20:19 | OK |
| 6 | 20 hz | 20:35 | OK, slight detour at 255855.01,6784094.03 |
| 7 | 20 hz | 21:17 | OK |


### February 16th 2022 (with snow):
| Trip# | Frequency | Start time | Comment |
|-------|-----------|------------|---------|
| 1 | 10 hz | 19:53 | OK |
| 2 | 10 hz | 20:04 | OK |
| 3 | 20 hz | 20:27 | OK, missing one PCAP file in the beginning, but we skip that part of the route in the analysis. |
| 4 | 20 hz | 20:38 | OK |
| 5 | 20 hz | 20:48 | OK |

## The analysis

### Method
The analysis was performed by processing the PCAP files for each of the collected trips, and using absolute or incremental navigation to estimate a position for each frame until navigation failure. Navigation failure is defined as when the estimated position is more than five meters from the correct position. 

The rest of this section is about Lillehammer specifically. See [this document](./../../_notes/summary.md) for more method details that are common for all four locations.

To make the results comparable, the trip analyses all started at the same point, which is set to after the missing PCAP file of trip 3 in 2022. This point is indicated with the blue circle on the image above. The analyses ran until failure, or until all frames were processed. In the next run, all analyses will end at before the last turn, almost straight north for the blue circle.

** Common command line arguments: **
```
{
	"sbet-z-offset": -39.416,
	"preview": "always",
	"build-cloud-after": 5,
	"skip-until-x": 579490.13,
	"skip-until-y": 6776060.22,
	"recreate-caches": true,
	"max-frame-radius": 25,
	"wait-after-first-frame": 0,
	"hide-point-cloud": true,
	"save-after-first-frame": true,
	"save-after-frames": 50
}
```

### Absolute navigation

The absolute navigation tables show how well the navigation worked in each of the four weather situations:
 - Bare/Bare means that the trips from 2021 (without snow) are run against the point cloud from 2021 (without snow).
 - Bare/Snow means that the trips from 2021 (without snow) are run against the point cloud from 2022 (with snow).
 - Snow/Bare means that the trips from 2022 (with snow) are run against the point cloud from 2021 (without snow).
 - Snow/Snow means that the trips from 2022 (with snow) are run against the point cloud from 2022 (with snow).

The numbers in the four results column represents the results for that combination, and are explained before each of the tables. Letters in those columns mean:
- N/A: This trip does not exist in this source material.
- N/P: This trip has not yet been processed.

_**Meters driven before failure**_

All entries with ~3500 meters did complete the entire route, but because of variances in the stopping point of the data collections, the lengths vary slightly.


| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 24.640 | 3,080.423 |
| 2     | N/A | N/A | 50.554 | 3,218.582 |
| 3     | 3,540.214 | 29.578 | 3,817.083 | 1,252.966 |
| 4     | 3,508.586 | 48.908 | 2,035.012 | N/P |
| 5     | 3,559.483 | 391.129 | 1,905.716 | N/P |
| 6     | 3,533.513 | 443.580 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **3,535.449** | **228.299** | **1,566.601** | **2,517.324** |

_**2D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 1.088 | 0.767 |
| 2     | N/A | N/A | 1.196 | 0.820 |
| 3     | 0.580 | 0.972 | 0.856 | 0.921 |
| 4     | 0.593 | 1.606 | 0.824 | N/P |
| 5     | 0.545 | 1.038 | 0.868 | N/P |
| 6     | 0.527 | 1.039 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.562** | **1.164** | **0.966** | **0.836** |

_**3D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 1.245 | 0.925 |
| 2     | N/A | N/A | 1.310 | 0.954 |
| 3     | 0.650 | 1.136 | 0.957 | 1.039 |
| 4     | 0.674 | 1.714 | 0.942 | N/P |
| 5     | 0.622 | 1.150 | 0.972 | N/P |
| 6     | 0.619 | 1.160 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.641** | **1.290** | **1.085** | **0.973** |

_**Reported registration fitness**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.966 | 0.998 |
| 2     | N/A | N/A | 0.964 | 1.000 |
| 3     | 0.984 | 0.904 | 0.982 | 1.000 |
| 4     | 0.889 | 0.976 | 0.979 | N/P |
| 5     | 0.985 | 0.998 | 0.983 | N/P |
| 6     | 0.900 | 0.998 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.940** | **0.969** | **0.975** | **0.999** |

_**Reported registration RMSE**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.200 | 0.065 |
| 2     | N/A | N/A | 0.188 | 0.050 |
| 3     | 0.073 | 0.186 | 0.126 | 0.048 |
| 4     | 0.102 | 0.202 | 0.128 | N/P |
| 5     | 0.076 | 0.131 | 0.120 | N/P |
| 6     | 0.092 | 0.132 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.086** | **0.163** | **0.152** | **0.054** |

_**Registration iterations before convergence**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 200.000 | 79.519 |
| 2     | N/A | N/A | 200.000 | 78.409 |
| 3     | 199.971 | 200.000 | 199.902 | 78.333 |
| 4     | 200.000 | 156.731 | 63.175 | N/P |
| 5     | 199.910 | 96.818 | 63.034 | N/P |
| 6     | 199.938 | 94.457 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **199.955** | **137.001** | **145.222** | **78.754** |

_**Links to individual trip details**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2022%2C%20PC2021/1_10hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2022%2C%20PC2022/1_10hz) |
| 2     | N/A | N/A | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2022%2C%20PC2021/2_10hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2022%2C%20PC2022/2_10hz) |
| 3     | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2021%2C%20PC2021/3_10hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2021%2C%20PC2022/3_10hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2022%2C%20PC2021/3_20hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2022%2C%20PC2022/3_20hz) |
| 4     | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2021%2C%20PC2021/4_10hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2021%2C%20PC2022/4_10hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2022%2C%20PC2021/4_20hz) | N/P |
| 5     | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2021%2C%20PC2021/5_20hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2021%2C%20PC2022/5_20hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2022%2C%20PC2021/5_20hz) | N/P |
| 6     | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2021%2C%20PC2021/6_20hz) | [Link](https://github.com/erlenddahl/teapot-lidar/tree/main/validation/Lillehammer/results/ABS%2C%20PCAP2021%2C%20PC2022/6_20hz) | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
