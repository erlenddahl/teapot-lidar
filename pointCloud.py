import os
import laspy
import numpy as np
import open3d as o3d
import argparse

from tqdm import tqdm
from open3dVisualizer import Open3DVisualizer

class PointCloudPart:

    def __init__(self, location):
        self.location = location
        self.file = laspy.open(location)

    def is_relevant(self, x, y):
        return self.file.header.x_min < x and self.file.header.x_max > x and self.file.header.y_min < y and self.file.header.y_max > y

    def load(self):
        self.contents = laspy.read(self.location)
        return self.contents

    def unload(self):
        self.contents = None

class PointCloud:

    def __init__(self, point_cloud_location):
        self.location = point_cloud_location
        self.visualizer = Open3DVisualizer()
        self.files = [PointCloudPart(os.path.join(self.location, x)) for x in os.listdir(self.location) if x.lower().endswith(".laz")]

    def get_relevant(self, x, y):

        for f in self.files:
            if True:#f.is_relevant(x, y):
                yield f.load()
            else:
                pass #f.unload()

    def to_absolute(self, vector, min):
        min = int(min)
        return min + vector / 1000.0

    def read_all(self, preview = 'never', max_files = -1):

        full_cloud = o3d.geometry.PointCloud()

        files = [x for x in os.listdir(self.location) if x.lower().endswith(".laz")]

        if max_files > 0 and len(files) > max_files:
            files = files[0:max_files]
        
        for file in tqdm(files, "Reading point cloud"):
            full_path = os.path.join(self.location, file)
            if os.path.isfile(full_path):
                
                # Read the .laz file (which is one part of the total point cloud)
                las = laspy.read(full_path)

                # Transform coordinates to fit the actual coordinate system
                x = self.to_absolute(las.X, las.header.x_min)
                y = self.to_absolute(las.Y, las.header.y_min)
                z = self.to_absolute(las.Z, las.header.z_min)

                # Merge X, Y and Z values together to a 3D array
                point_data = np.stack([x, y, z], axis=0).transpose((1, 0))

                # Create an open3d point cloud
                partial_cloud = o3d.geometry.PointCloud()
                partial_cloud.points = o3d.utility.Vector3dVector(point_data)

                full_cloud += partial_cloud

                if preview == 'always':
                    self.visualizer.show_frame(full_cloud)
                    self.visualizer.refresh_non_blocking()

        if preview != 'never':
            #self.visualizer.show_frame(full_cloud)
            #self.visualizer.run()
            o3d.visualization.draw_geometries([full_cloud])

        return full_cloud


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--point-cloud', type=str, required=True, help="A directory containing the point cloud as .laz files.")
    parser.add_argument('--preview', type=str, default="never", choices=['always', 'end', 'never'], help="Show constantly updated point cloud and data plot previews while processing ('always'), show them only at the end ('end'), or don't show them at all ('never').")
    parser.add_argument('--max-files', type=int, default=-1, help="Stop reading after the given number of files.")
    parser.add_argument('--write-to', type=str, default=None, help="Write the assembled point cloud to this location.")

    args = parser.parse_args()

    reader = PointCloud(args.point_cloud)
    cloud = reader.read_all(args.preview, args.max_files)

    if args.write_to is not None:
        o3d.io.write_point_cloud(args.write_to, cloud, compressed=True)