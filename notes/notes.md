# Notes
Contains informal notes made during experimentation and development, as well as some plans for future work.

## Reducing the number of points
As point clouds are rather large (usually at least a 100 000 points per frame), doing work on them can be time consuming. By reducing the number of points, we can speed up most calculations.

## Tracking movements between two LIDAR frames
In order to track movements between two LIDAR frames, we need to use some kind of feature matching to detect similar features in the two frames, and calculate how much they have moved.

In the point cloud literature, it looks like [ICP (Iterative Closest Point)](https://en.wikipedia.org/wiki/Iterative_closest_point) registration is the way to go. The ICP registration algorithm "has been a mainstay of geometric registration in both research and industry for many years", according to the [open3d documentation](http://www.open3d.org/docs/release/tutorial/pipelines/icp_registration.html).

During experimentation, we tested both [pyoints](https://github.com/laempy/pyoints)' ICP implementation, and open3d's [implementation](http://www.open3d.org/docs/release/tutorial/pipelines/icp_registration.html). Both libraries supports both ICP and NICP (which uses normals, or a point-to-plane objective function, to improve the convergence speed).

__TODO__: Include test results from pyoints ICP/NICP and open3d with and without downsampling.

As open3d was faster, easier to work with, and still regularly updated, it was an easy choice.

# Future work
Test [multiway registration](http://www.open3d.org/docs/latest/tutorial/pipelines/multiway_registration.html).

And/or: combine open3d-icp with [global registration](http://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html) for speed-up.

Remove vehicle from point cloud:
```
vr = 2.5
A = A[((A[:, 0] > vr) | (A[:, 0] < -vr)) | ((A[:, 1] > vr) | (A[:, 1] < -vr))]
```