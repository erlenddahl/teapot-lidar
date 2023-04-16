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
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 24.640 | 2,630.914 |
| 2     | N/A | N/A | 50.554 | 2,945.924 |
| 3     | 3,540.214 | 29.578 | 3,817.083 | 1,252.966 |
| 4     | 3,508.586 | 48.908 | 2,035.012 | N/P |
| 5     | 3,559.483 | 148.795 | 1,905.716 | N/P |
| 6     | 3,533.513 | 183.769 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **3,535.449** | **102.763** | **1,566.601** | **2,276.601** |

_**2D difference between actual and estimated coordinates [M]**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 1.088 | 0.795 |
| 2     | N/A | N/A | 1.196 | 0.833 |
| 3     | 0.580 | 0.972 | 0.856 | 0.921 |
| 4     | 0.593 | 1.606 | 0.824 | N/P |
| 5     | 0.545 | 0.848 | 0.868 | N/P |
| 6     | 0.527 | 0.873 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.562** | **1.075** | **0.966** | **0.850** |

_**Reported registration fitness**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.966 | 0.998 |
| 2     | N/A | N/A | 0.964 | 1.000 |
| 3     | 0.984 | 0.904 | 0.982 | 1.000 |
| 4     | 0.889 | 0.976 | 0.979 | N/P |
| 5     | 0.985 | 1.000 | 0.983 | N/P |
| 6     | 0.900 | 0.999 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.940** | **0.970** | **0.975** | **0.999** |

_**Reported registration RMSE**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 0.200 | 0.066 |
| 2     | N/A | N/A | 0.188 | 0.050 |
| 3     | 0.073 | 0.186 | 0.126 | 0.048 |
| 4     | 0.102 | 0.202 | 0.128 | N/P |
| 5     | 0.076 | 0.128 | 0.120 | N/P |
| 6     | 0.092 | 0.126 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **0.086** | **0.160** | **0.152** | **0.055** |

_**Registration iterations before convergence**_
| Trip#   | Bare/Bare | Bare/Snow | Snow/Bare | Snow/Snow |
|---------|-----------|-----------|-----------|-----------|
| 1     | N/A | N/A | 200.000 | 78.599 |
| 2     | N/A | N/A | 200.000 | 78.976 |
| 3     | 199.971 | 200.000 | 199.902 | 78.333 |
| 4     | 200.000 | 156.731 | 63.175 | N/P |
| 5     | 199.910 | 107.714 | 63.034 | N/P |
| 6     | 199.938 | 106.625 | N/A | N/A |
| 7     | N/P | N/P | N/A | N/A |
| **Average** | **199.955** | **142.768** | **145.222** | **78.636** |