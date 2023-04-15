# Summary
Four sites, two data collections, 6-8 trips each time, about half of the trips with 10hz, and the other half with 20hz.
Collected LiDAR data using an X, stored as PCAP files, and GNSS coordinates using a Y, stored as SBET files. Coordinates from the SBET files were matched against LiDAR frames in the PCAP files using their timestamps.

## Differences between 10hz and 20hz
The PCAP files with 20hz have approximately 0.135 meters between frames (depending on driving speed). The 10hz files have approximately double that (often closer to 0.300 meters).
[10hz_vs_20hz.png]

10hz can be simulated from 20hz files by running them with --skip-every-frame 1, which makes the navigator skip every second frame. This was tested on a few runs of the Lillehammer 2021 dataset, and showed that [TODO: conclusion]

## Data recording limitations
The data collection system ran in a loop that recorded LiDAR frames for 20 seconds, then saved them disk, then recorded for next 20 seconds, etc. This resulted in a slight gap between the files of about 1 to 1.5 seconds, or usually around 5-7 meters (depending on driving speed).
[file_gap.png]

To avoid registration problems every time the analysis progressed from one file to the next, the current position estimate is always translated to have the same offset from the first actual coordinate in the next file, as it had from the last actual coordinate in the previous file. This way, the analysis effectively skips the jump between the files.

## NICP parameters
The most important parameters to the NICP algorithm are the threshold, and the maximum number of iterations. The threshold limits how far away point in the source and target point clouds can be and still be considered matches. Too high values here causes less precise registrations, while too low values can cause two sequential PCAP frames to not get a registration at all if they are different enough. The Lillehammer dataset has been run with different values of the threshold parameter: the initial attempt was touse a dynamic threshold to allow the navigation to get back on track after errors, but this resulted in a relatively poor estimation of the driving route with multiple small jumps, and often failures within a few hundred meters. In the end, a threshold of 1 seems to give very good results, and at least when registering every frame in the PCAP file, there is no need for higher thresholds in order to get back on track (because it never leaves the track in the first place).
[find examples of tracks for 1 and 2]

The NICP algorithm also has input parameters that allows us to set a relative_fitness or relative_rmse value that can stop the iteration before it reaches max_iterations if the fitness/rmse change between iterations gets smaller than that. This is the easiest way of setting a convergence criteria. But since those values are very abstract, the navigators instead run NICP with a relatively low max_iterations of 25 repeatedly, until the change in the movement part of the transformation matrix results in a translation less than 1e-3 meters. 1e-5 was also tested, but doubled the run time with no noticeable increase in precision.
[APS PCAP22 PC22 2_10 (1e3) and 2_10_1e5]