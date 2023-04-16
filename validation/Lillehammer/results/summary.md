
# Lillehammer

## The collected datasets

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
| 2 | 10 hz | 20:04 | OK, navigation issues after 579295.42,6776465.81 |
| 3 | 20 hz | 20:27 | OK, missing one PCAP file in the beginning, but we skip that part of the route in the analysis. |
| 4 | 20 hz | 20:38 | OK |
| 5 | 20 hz | 20:48 | OK |

The image below shows the driving route on a map of Lillehammer. All 10 valid trips are drawn, but as they are very similar, it's hard to differentiate them in this plot. The brown detour on the right hand side is part of the 2021 trips -- they started at the parkin spot at the bottom end of the brown arm, and drove north before entering the standard route. The 2022 trips started approximately at the same spot, but drove west, directly entering the route. Because of this discrepancy, and because trip 2022-3 is missing a PCAP file, the analysis start point is set to be after all trips are driving the same route without issues (white circle), and because of the navigation issues in trip 2022-2, the end point is set to the last left turn (black circle).

![The driving route shown on a map.](full_route.png)

## The analysis

### Details

This section is about Lillehammer specifically. See [this document](./../../_notes/summary.md) for more method details that are common for all four locations.

To make the results comparable, the trip analyses all started at the same point, which is set to after the missing PCAP file of trip 3 in 2022. This point is indicated with the white circle on the image above. The analyses ran until failure, or until the actual position reached the end circle (black).

**Common command line arguments:**
```
{
	"sbet-z-offset": -39.416,
	"preview": "always",
	"build-cloud-after": 5,
	"skip-until-x": 579490.13,
	"skip-until-y": 6776060.22,
	"run-until-x": 579295.42,
	"run-until-y": 6776465.81,
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
| 1     | N/A | N/A | 24.640 | 3,172.350 |
| 2     | N/A | N/A | 50.554 | 3,176.430 |
| 3     | 3,017.985 | 29.578 | 3,195.761 | 2,094.734 |
| 4     | 3,006.294 | 48.908 | 3,070.650 | 265.707 |
| 5     | 3,030.820 | 719.536 | 2,973.419 | 272.403 |
| 6     | 3,013.980 | 742.330 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **3,017.270** | **385.088** | **1,863.005** | **1,796.325** |

_**2D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 1.088 | 0.774 |
| 2     | N/A | N/A | 1.196 | 0.816 |
| 3     | 0.573 | 0.972 | 0.844 | 0.898 |
| 4     | 0.582 | 1.606 | 0.809 | 0.958 |
| 5     | 0.540 | 1.012 | 0.860 | 0.972 |
| 6     | 0.527 | 1.015 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.556** | **1.151** | **0.959** | **0.884** |

_**3D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 1.245 | 0.933 |
| 2     | N/A | N/A | 1.310 | 0.951 |
| 3     | 0.650 | 1.136 | 0.948 | 1.011 |
| 4     | 0.671 | 1.714 | 0.936 | 1.002 |
| 5     | 0.624 | 1.144 | 0.970 | 1.018 |
| 6     | 0.628 | 1.150 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.643** | **1.286** | **1.082** | **0.983** |

_**Reported registration fitness**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.966 | 0.998 |
| 2     | N/A | N/A | 0.964 | 1.000 |
| 3     | 0.984 | 0.904 | 0.981 | 0.999 |
| 4     | 0.889 | 0.976 | 0.979 | 0.999 |
| 5     | 0.984 | 0.989 | 0.982 | 1.000 |
| 6     | 0.899 | 0.987 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.939** | **0.964** | **0.974** | **0.999** |

_**Reported registration RMSE**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.200 | 0.065 |
| 2     | N/A | N/A | 0.188 | 0.051 |
| 3     | 0.073 | 0.186 | 0.124 | 0.052 |
| 4     | 0.103 | 0.202 | 0.127 | 0.051 |
| 5     | 0.077 | 0.135 | 0.120 | 0.044 |
| 6     | 0.092 | 0.139 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.086** | **0.165** | **0.152** | **0.053** |

_**Registration iterations before convergence**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 200.000 | 79.138 |
| 2     | N/A | N/A | 200.000 | 78.574 |
| 3     | 199.965 | 200.000 | 199.887 | 74.169 |
| 4     | 200.000 | 156.731 | 63.961 | 98.467 |
| 5     | 199.896 | 85.143 | 63.772 | 99.200 |
| 6     | 199.927 | 84.488 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **199.947** | **131.590** | **145.524** | **85.910** |

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
