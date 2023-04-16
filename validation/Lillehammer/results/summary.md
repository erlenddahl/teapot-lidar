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

To make the results comparable, the trip analyses all started at the same point, which is set to after the missing PCAP file of trip 3 in 2022. This point is indicated with the white circle on the image above. The analyses ran until failure, or until the actual position reached the end circle (black).

**Common command line arguments:**
```
{
	"sbet-z-offset": -39.416,
	"preview": "always",
	"build-cloud-after": 5,
	"skip-until-x": 579490.13,
	"skip-until-y": 6776060.22,
	"run-until-x": 579523.26,
	"run-until-y": 6776424.83,
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
| 1     | N/A | N/A | 24.640 | 3,234.967 |
| 2     | N/A | N/A | 50.554 | 3,478.134 |
| 3     | 3,307.276 | 29.578 | 3,498.181 | 2,094.734 |
| 4     | 3,294.255 | 48.908 | 3,070.650 | 265.707 |
| 5     | 3,314.796 | 678.582 | 2,973.419 | 272.403 |
| 6     | 3,297.030 | 709.508 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **3,303.339** | **366.644** | **1,923.489** | **1,869.189** |

_**2D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 1.088 | 0.797 |
| 2     | N/A | N/A | 1.196 | 0.821 |
| 3     | 0.588 | 0.972 | 0.831 | 0.898 |
| 4     | 0.597 | 1.606 | 0.809 | 0.958 |
| 5     | 0.548 | 1.046 | 0.860 | 0.972 |
| 6     | 0.534 | 1.038 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.567** | **1.166** | **0.957** | **0.889** |

_**3D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 1.245 | 0.954 |
| 2     | N/A | N/A | 1.310 | 0.953 |
| 3     | 0.660 | 1.136 | 0.935 | 1.011 |
| 4     | 0.681 | 1.714 | 0.936 | 1.002 |
| 5     | 0.627 | 1.176 | 0.970 | 1.018 |
| 6     | 0.629 | 1.171 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.649** | **1.299** | **1.079** | **0.988** |

_**Reported registration fitness**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.966 | 0.998 |
| 2     | N/A | N/A | 0.964 | 1.000 |
| 3     | 0.984 | 0.904 | 0.982 | 0.999 |
| 4     | 0.891 | 0.976 | 0.979 | 0.999 |
| 5     | 0.985 | 0.989 | 0.982 | 1.000 |
| 6     | 0.901 | 0.986 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.940** | **0.964** | **0.975** | **0.999** |

_**Reported registration RMSE**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.200 | 0.065 |
| 2     | N/A | N/A | 0.188 | 0.050 |
| 3     | 0.073 | 0.186 | 0.124 | 0.052 |
| 4     | 0.103 | 0.202 | 0.127 | 0.051 |
| 5     | 0.077 | 0.136 | 0.120 | 0.044 |
| 6     | 0.092 | 0.141 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.086** | **0.166** | **0.152** | **0.053** |

_**Registration iterations before convergence**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 200.000 | 79.054 |
| 2     | N/A | N/A | 200.000 | 79.050 |
| 3     | 199.968 | 200.000 | 199.896 | 74.169 |
| 4     | 200.000 | 156.731 | 63.961 | 98.467 |
| 5     | 199.904 | 85.987 | 63.772 | 99.200 |
| 6     | 199.934 | 85.225 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **199.951** | **131.986** | **145.526** | **85.988** |

_**Links to individual trip details**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/1_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/1_10hz) |
| 2     | N/A | N/A | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/2_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/2_10hz) |
| 3     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/3_10hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/3_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/3_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/3_20hz) |
| 4     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/4_10hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/4_10hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/4_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/4_20hz) |
| 5     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/5_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/5_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2021/5_20hz) | [Link](./ABS%2C%20PCAP2022%2C%20PC2022/5_20hz) |
| 6     | [Link](./ABS%2C%20PCAP2021%2C%20PC2021/6_20hz) | [Link](./ABS%2C%20PCAP2021%2C%20PC2022/6_20hz) | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
