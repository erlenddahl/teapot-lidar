Summary
Four sites, two data collections, 6-8 trips each time.
Collected LiDAR data using an X, stored as PCAP files, and GNSS coordinates using a Y, stored as SBET files. Coordinates from the SBET files were matched against LiDAR frames in the PCAP files using their timestamps.

Differences 10hz vs 20hz
20hz approximately 0.135 meters between frames (depends on driving speed).
10hz approximately 0.300 meters between frames.
[10hz_vs_20hz.png]

Data recording limitations
The data collection system ran in a loop that recorded LiDAR frames for 20 seconds, then saved them disk, then recorded for next 20 seconds, etc. This resulted in a slight gap between the files of about 1 to 1.5 seconds, or usually around 5-7 meters (depending on driving speed).
[file_gap.png]

To avoid registration problems every time the analysis progressed from one file to the next, the current position estimate is always translated to have the same offset from the first actual coordinate in the next file, as it had from the last actual coordinate in the previous file. This way, the analysis effectively skips the jump between the files.