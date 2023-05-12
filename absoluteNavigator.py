from navigatorBase import NavigatorBase
import numpy as np
import os
from tqdm import tqdm
import open3d as o3d
from datetime import datetime
import copy
import json

class AbsoluteLidarNavigator(NavigatorBase):

    def __init__(self, args):
        """Initialize an AbsoluteLidarNavigator by reading metadata and setting
        up a package source from the pcap file.
        """

        NavigatorBase.__init__(self, args, 0)

        self.load_point_cloud(args.point_cloud)

        if self.args.sbet is None:
            raise Exception("Absolute navigation must have SBET coordinates (--sbet).")

    def load_point_cloud(self, path):

        cloud_meta_data_path = path.replace(".pcd", "-meta.json")

        with tqdm(total=1, desc="Loading point cloud", **self.tqdm_config) as pbar:

            with open(cloud_meta_data_path, "r") as outfile:
                data = json.load(outfile)

            self.full_point_cloud_offset = np.array([data["offset"][0], data["offset"][1], data["offset"][2]])
            self.full_cloud = o3d.io.read_point_cloud(path)

            self.full_cloud.paint_uniform_color([0.3, 0.6, 1.0])

            pbar.update(1)

        tqdm.write("Point cloud metadata:")
        tqdm.write(json.dumps(data, indent=4, sort_keys=True))

    def navigate_through_file(self):
        """ Runs through each frame in the file. For each pair of frames, use NICP
        to align the frames, then merge them and downsample the result. The transformation
        matrix from the NICP operation is used to calculate the movement of the center point
        (the vehicle) between the frames. Each movement is stored, and drawn as a red line
        to show the driving route.
        """
        
        self.initialize_navigation(rotate_sbet=False)

        self.last_extracted_frame_coordinate = None
        self.last_extracted_frame = None
        
        # Initialize the visualizer
        self.initialize_plot_and_visualization()

        if self.preview_always:
            self.vis.refresh_non_blocking()

            if not self.args.hide_point_cloud:
                self.vis.show_frame(self.full_cloud)

        self.is_first_frame = True

        navigation_exception = None

        # Enumerate all frames until the end of the file and run the merge operation.
        for i in tqdm(range(1, self.frame_limit), total=self.frame_limit, initial=1, **self.tqdm_config):
            
            try:
                
                if self.args.use_actual_coordinate:
                    self.current_estimated_coordinate = actual_coordinate.clone()

                if self.merge_next_frame():

                    # Refresh the non-blocking visualization
                    if self.preview_always:
                        self.vis.refresh_non_blocking()
                        self.vis.update_geometry(self.actual_position_cylinder)
                        self.vis.update_geometry(self.estimated_position_cylinder)
                        self.vis.update_geometry(self.start_position_cylinder)

                        self.time("visualization refresh")

                        self.check_save_screenshot(i)

                    self.check_wait()

            except Exception as e:

                navigation_exception = e
                
                break
        
        return self.finalize_navigation(navigation_exception)

    def draw_registration_result(self, source, target):
        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        o3d.visualization.draw_geometries([source_temp, target_temp])

    def throw_outside_of_cloud(self, actual_position, partial_radius):
        print("")
        print("")
        self.print_cloud_info("Cloud", self.full_cloud, "    ")
        print("Current position:", actual_position)
        print("Radius:", partial_radius)
        raise Exception("The point cloud contains no points around the current position.")

    def merge_next_frame(self):
        """ Reads the next frame, aligns it with the previous frame, merges them together
        to create a 3D model, and tracks the movement between frames.
        """

        # Fetch the next frame
        frame = self.reader.next_frame(self.remove_vehicle, self.timer, False)

        self.time("frame extraction")

        # If it is empty, that (usually) means we have reached the end of
        # the file. Return False to stop the loop.
        if frame is None:
            return False

        if self.run_until_ix > 0 and self.reader.get_current_frame_index() >= self.run_until_ix:
            return False

        # Find the current position, and update the blue (actual) position cylinder
        actual_coordinate = self.get_current_actual_coordinate().clone()
        self.actual_position_cylinder.translate(actual_coordinate.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)

        # If this is the first frame in a new file (but not in the very first file), we want to move the 
        # current position to avoid the results getting messed up by the (relatively) large gap between files.
        if self.reader.is_first_frame_in_file() and not self.is_first_frame:
            
            # Extract the last estimated and actual coordinates
            last_estimate = self.estimated_coordinates[-1]
            last_actual = self.actual_coordinates[-1]

            # Calculate the current estimation offset
            dx = last_estimate.x - last_actual.x
            dy = last_estimate.y - last_actual.y
            dz = last_estimate.alt - last_actual.alt

            # Now just move the estimate so that it is offset with the same amount, but from the
            # first coordinate in the new file instead of the last coordinate in the last file.
            self.current_estimated_coordinate = actual_coordinate.clone().translate([dx, dy, dz])

        if self.is_first_frame:
            self.is_first_frame = False

        self.time("position extraction")

        # Extract a part of the cloud around the actual position. This is the cloud we are going to register against.
        partial_radius = self.args.cloud_part_radius
        pr = np.array([partial_radius, partial_radius, partial_radius])

        previous_estimated_coordinate = self.current_estimated_coordinate.clone()

        # Keep a slightly larger partial cloud to make it quicker to extract the actual partial cloud
        # This reduced time usage from 27 to 9 seconds on first 20 frames of a random file.
        c = previous_estimated_coordinate.np()

        if self.last_extracted_frame_coordinate is None or self.last_extracted_frame_coordinate.distance2d(self.current_estimated_coordinate) >= partial_radius * 0.8:

            bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=c - pr * 2, max_bound=c + pr * 2)
            self.last_extracted_frame = self.full_cloud.crop(bbox)
            self.last_extracted_frame_coordinate = self.current_estimated_coordinate.clone()
           
            self.time("larger partial cloud point extraction")

        bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=c - pr, max_bound=c + pr)
        partial_cloud = self.last_extracted_frame.crop(bbox)

        if len(partial_cloud.points) < 10:
            self.throw_outside_of_cloud(self.current_estimated_coordinate, partial_radius)
        
        self.time("partial cloud point extraction")

        if self.preview_always:
            partial_cloud_visualization = self.modify_cloud(partial_cloud, translate=[0,0,0.1], voxel_size=0.5, color=[1,0,0])
            self.vis.add_geometry(partial_cloud_visualization, update=True)
            self.time("partial cloud visualization")
        
        # Move the points so that the current coordinate is in the origin.
        # Now, both the current frame and this part of the cloud should be positioned very close to each other around the origin.
        partial_cloud_transform = c
        partial_cloud.translate(-partial_cloud_transform, relative = True)
        self.time("partial cloud point movement")

        # Estimate normals for the target frame
        frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("frame normal estimation")

        reg = self.run_registration(frame, partial_cloud, previous_estimated_coordinate, actual_coordinate)

        # Update the visualization
        if self.preview_always:
            self.vis.remove_geometry(partial_cloud_visualization)
            self.time("visualization")

        if self.build_cloud:
            transformed_frame = frame.transform(reg.transformation)
            transformed_frame.translate(partial_cloud_transform, relative=True)
            transformed_frame.paint_uniform_color([0,1,0])

            self.add_to_merged_frame(transformed_frame, handle_visualization=True)

            #self.vis.set_follow_vehicle_view(self.current_estimated_coordinate.np())

        # Return True to let the loop continue to the next frame.
        return True
        

if __name__ == "__main__":

    parser = NavigatorBase.create_parser()

    parser.add_argument('--point-cloud', type=str, required=True, help="An Open3D point cloud file to use for absolute navigation, preferably generated by pointCloud.py. Every frame in the PCAP file(s) is registered against this point cloud in order to geolocate the frames.")
    parser.add_argument('--hide-point-cloud', dest='hide_point_cloud', default=False, action='store_true', help="If set to true, the full point cloud will not be displayed in the visualization. Can be useful for a visualization performance boost, or if the frames drawn together with the cloud gets too chaotic.")
    parser.add_argument('--cloud-part-radius', type=float, default=30, required=False, help="The radius of the part of the cloud that is extracted for local registration -- frames are registered against these extracted parts of the full cloud, as registration against the full cloud is very time consuming, and gives poor results.")
    
    args = NavigatorBase.add_standard_and_parse_args(parser)

    # Create and start a visualization
    navigator = AbsoluteLidarNavigator(args)
    navigator.print_summary_at_end = True
    navigator.navigate_through_file()