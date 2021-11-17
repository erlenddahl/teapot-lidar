# Notes
Contains informal notes made during experimentation and development, as well as some plans for future work.

## Reading LIDAR data
The data used in the project are recorded using an Ouster lidar, which stores data as .pcap files with corresponding .json files containing sensor metadata. These files can be read using the [Ouster SDK](https://static.ouster.dev/sdk-docs/quickstart.html). This is done in `pcapReader.py`, whose `readFrame()` and `nextFrame()` functions returns a numpy array of points (which are numpy arrays of length 3; x, y and z).

## Reducing the number of points (downsampling)
As point clouds are rather large (usually at least a 100 000 points per frame), doing work on them can be time consuming. By reducing the number of points, we can speed up most calculations.

## Tracking movements between two LIDAR frames
In order to track movements between two LIDAR frames, we need to use some kind of feature matching to detect similar features in the two frames, and calculate how much they have moved.

In the point cloud literature, it looks like [ICP (Iterative Closest Point)](https://en.wikipedia.org/wiki/Iterative_closest_point) registration is the way to go. The ICP registration algorithm "has been a mainstay of geometric registration in both research and industry for many years", according to the [open3d documentation](http://www.open3d.org/docs/release/tutorial/pipelines/icp_registration.html).

During experimentation, we tested both [pyoints](https://github.com/laempy/pyoints)' ICP implementation, and open3d's [implementation](http://www.open3d.org/docs/release/tutorial/pipelines/icp_registration.html). Both libraries supports both ICP and NICP (which uses normals, or a point-to-plane objective function, to improve the convergence speed).

The table below shows some test results for ICP and NICP from Pyoints and Open3d. Note that Open3d's "point-to-point" corresponds to Pyoints' ICP, while "point-to-plane" corresponds to NICP. The maximum number of iterations was 100, and the convergence threshold was 0.001. Only Open3d reported fitness values. Open3d reported "inlier_rmse", while Pyoints reported "RMSE" -- they may not be comparable (according to visual comparisons of the matched frames, they are not). Open3d did not report the number of iterations used. The time usage for Open3d point-to-plane includes normal calculations, which seems to take well below 0.1 seconds per cloud (presumably depending on point count).

Screenshots of original frames as well as matched frames for all rows in the table below can be found in the notes folder, prefixed with "frame-matching".

| Function       | Downsampling | Iterations | Time usage | RMSE    | Fitness | Movement distance (xyz) |
|----------------|--------------|------------|------------|---------|---------|-------------------|
| Pyoints ICP    | No           | 60         | 200.6 s    | 0.0025  | -       | 0.68, 0.19, 0.03  |
| Pyoints NICP   | No           | 46         | 173.5 s    | 0.0019  | -       | 0.65, 0.19, 0.02  |
| Pyoints ICP    | 0.5          | 85         | 65.4 s     | 0.0025  | -       | 0.69, 0.20, 0.04  |
| Pyoints NICP   | 0.5          | 48         | 9.7 s      | 0.0026  | -       | 0.70, 0.17, 0.04  |
| Open3d p2point | No           | ?          | 1.1 s      | 0.1554  | 0.9914  | 0.64, 0.12, 0.04  |
| Open3d p2plane | No           | ?          | 0.8 s      | 0.1521  | 0.9908  | 0.68, 0.15, 0.04  |

| Library | Radius | Time usage |
|---------|--------|------------|
| Pyoints | 0.5    | 0.389 s    |

As open3d was faster, easier to work with, and still regularly updated, it was an easy choice.

# Future work
Test [multiway registration](http://www.open3d.org/docs/latest/tutorial/pipelines/multiway_registration.html).

And/or: combine open3d-icp with [global registration](http://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html) for speed-up.

Remove vehicle from point cloud:
```
vr = 2.5
A = A[((A[:, 0] > vr) | (A[:, 0] < -vr)) | ((A[:, 1] > vr) | (A[:, 1] < -vr))]
```