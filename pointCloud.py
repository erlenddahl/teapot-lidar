import os
import json
import laspy
import numpy as np
import open3d as o3d
import argparse

from tqdm import tqdm
from utils.open3dVisualizer import Open3DVisualizer

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
        self.common_offsets = []

    def get_relevant(self, x, y):

        for f in self.files:
            if True:#f.is_relevant(x, y):
                yield f.load()
            else:
                pass #f.unload()

    def to_absolute(self, vector, lowest):
        return int(lowest) + vector / 1000.0

    def read_all(self, preview = 'never', max_files=-1, voxel_size=None):

        full_cloud = o3d.geometry.PointCloud()

        # List all .laz files in the given directory
        files = [os.path.join(self.location, x) for x in os.listdir(self.location) if x.lower().endswith(".laz")]

        if max_files > 0 and len(files) > max_files:
            files = files[0:max_files]

        offsets = []
        for file in tqdm(files, "Calculating common offset"):
            # Use laspy.open to read only the header, and extract the min values.
            with laspy.open(file) as las:
                offsets.append([las.header.x_min, las.header.y_min, las.header.z_min])

        x_min_all = min([x[0] for x in offsets])
        y_min_all = min([x[1] for x in offsets])
        z_min_all = min([x[2] for x in offsets])

        self.common_offset = [x_min_all, y_min_all, z_min_all]
        
        for file in tqdm(files, "Reading point cloud"):
                
            # Read the .laz file (which is one part of the total point cloud)
            las = laspy.read(file)

            # Transform coordinates to fit the actual coordinate system
            x = self.to_absolute(las.X, las.header.x_min - x_min_all)
            y = self.to_absolute(las.Y, las.header.y_min - y_min_all)
            z = self.to_absolute(las.Z, las.header.z_min - z_min_all)

            # Merge X, Y and Z values together to a 3D array
            point_data = np.stack([x, y, z], axis=0).transpose((1, 0))

            # Create an open3d point cloud
            partial_cloud = o3d.geometry.PointCloud()
            partial_cloud.points = o3d.utility.Vector3dVector(point_data)

            full_cloud += partial_cloud

            if preview == 'always':
                self.visualizer.show_frame(full_cloud)
                self.visualizer.refresh_non_blocking()

        if voxel_size is not None:
            self.original_point_count = len(full_cloud.points)
            full_cloud = full_cloud.voxel_down_sample(voxel_size=voxel_size)
            self.downsampled_point_count = len(full_cloud.points)

        if preview != 'never':
            #self.visualizer.show_frame(full_cloud)
            #self.visualizer.run()
            o3d.visualization.draw_geometries([full_cloud])

        points = np.asarray(full_cloud.points)
        self.cloud_mins = np.amin(points, axis=0)
        self.cloud_maxes = np.amax(points, axis=0)
        self.full_point_cloud_offset = (self.cloud_maxes - self.cloud_mins) / 2
        
        points -= self.full_point_cloud_offset
        full_cloud = o3d.geometry.PointCloud()
        full_cloud.points = o3d.utility.Vector3dVector(points)

        self.total_offset = [self.common_offset[0] + self.full_point_cloud_offset[0], self.common_offset[1] + self.full_point_cloud_offset[1], self.common_offset[2] + self.full_point_cloud_offset[2]]

        return full_cloud


def load_point_cloud(path):

    full_cloud = o3d.io.read_point_cloud(path)
    full_cloud.paint_uniform_color([0.3, 0.6, 1.0])

    o3d.visualization.draw_geometries([full_cloud])

def process_args(args):
    if args.show is not None:
        load_point_cloud(args.show)
        return

    if args.create_from is None or args.create_from == "":
        raise Exception("The following arguments are required unless --show is given: --create-from")
        return

    reader = PointCloud(args.create_from)
    cloud = reader.read_all(args.preview, args.max_files, args.voxel_size)

    if args.write_to is not None:
        print("Writing .pcd ...")
        cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        o3d.io.write_point_cloud(args.write_to, cloud, compressed=False)
        with open(args.write_to.replace(".pcd", "-meta.json"), "w") as outfile:
            metadata = { 
                "offset": reader.total_offset, 
                "common_offset": reader.common_offset, 
                "point_cloud_offset": reader.full_point_cloud_offset.tolist(), 
                "mins": reader.cloud_mins.tolist(), 
                "maxes": reader.cloud_maxes.tolist()
            }
            if args.voxel_size is not None:
                metadata["voxel_size"] = args.voxel_size
                metadata["original_point_count"] = reader.original_point_count
                metadata["downsampled_point_count"] = reader.downsampled_point_count
            json.dump(metadata, outfile)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--create-from', type=str, help="A directory containing the point cloud as .laz files.")
    parser.add_argument('--voxel-size', type=float, default=None, help="If given, the point cloud will be downsampled with this voxel size.")
    parser.add_argument('--preview', type=str, default="never", choices=['always', 'end', 'never'], help="Show constantly updated point cloud and data plot previews while processing ('always'), show them only at the end ('end'), or don't show them at all ('never').")
    parser.add_argument('--max-files', type=int, default=-1, help="Stop reading after the given number of files (useful for saving time while testing).")
    parser.add_argument('--write-to', type=str, default=None, help="Write the assembled point cloud to this location.")
    parser.add_argument("--show", type=str, help="A .pcd file to show -- will not do any processing, just show it.")

    args = parser.parse_args()

    process_args(args)