from open3dVisualizer import Open3DVisualizer
from navigatorBase import NavigatorBase
from plotter import Plotter
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
        
        self.position_cylinder_radius = 1
        self.position_cylinder_height = 20

        self.load_point_cloud(args.point_cloud)

        NavigatorBase.__init__(self, args, 0)

        self.merged_frame = None

    def load_point_cloud(self, path):

        cloud_meta_data_path = path.replace(".pcd", "-meta.json")

        print("Loading point cloud ...")

        with open(cloud_meta_data_path, "r") as outfile:
            data = json.load(outfile)

        self.full_point_cloud_offset = np.array([data["offset"][0], data["offset"][1], data["offset"][2]])
        self.full_cloud = o3d.io.read_point_cloud(path)

        self.full_cloud.paint_uniform_color([0.3, 0.6, 1.0])

        print("    > Cloud loaded")

    def navigate_through_file(self):
        """ Runs through each frame in the file. For each pair of frames, use NICP
        to align the frames, then merge them and downsample the result. The transformation
        matrix from the NICP operation is used to calculate the movement of the center point
        (the vehicle) between the frames. Each movement is stored, and drawn as a red line
        to show the driving route.
        """
        
        self.timer.reset()
        self.skip_initial_frames()

        # Initialize the list of movements as well as the merged frame, and the first 
        # source frame.
        self.movements = []
        self.registration_configs = []

        self.movement_path = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector([]), lines=o3d.utility.Vector2iVector([])
        )

        if args.sbet is not None:

            # Read the coordinates from all frames in the PCAP file(s).
            # We set the rotate-argument to False, since we're working with
            # the same coordinate system here -- both the georeferenced point cloud
            # and the actual coordinates of the frames are in UTM, and there is
            # therefore no need to rotate them like it is in the visual odometry
            # based navigator.
            self.sbet_coordinates = self.reader.get_coordinates(False, show_progress=True)
            self.actual_coordinates = []
            self.estimated_coordinates = []

            # Translate all coordinates towards origo with the same offset as
            # the point cloud.
            for c in self.sbet_coordinates:
                c.translate(-self.full_point_cloud_offset)
            
            self.current_coordinate = self.sbet_coordinates[0].clone()
            self.initial_coordinate = self.sbet_coordinates[0].clone()

            self.actual_movement_path = o3d.geometry.LineSet(
                points = o3d.utility.Vector3dVector([[p.x, p.y, p.alt] for p in self.sbet_coordinates]), 
                lines = o3d.utility.Vector2iVector([[i, i+1] for i in range(len(self.sbet_coordinates) - 1)])
            )
            self.actual_movement_path.paint_uniform_color([0, 0, 1])
            
            self.actual_position_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=self.position_cylinder_radius, height=self.position_cylinder_height, resolution=20, split=4)
            self.actual_position_cylinder.paint_uniform_color([0.0, 0.0, 1.0])
            
            self.estimated_position_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=self.position_cylinder_radius * 0.8, height=self.position_cylinder_height * 1.2, resolution=20, split=4)
            self.estimated_position_cylinder.paint_uniform_color([1.0, 0.0, 0.0])
            
            self.start_position_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=self.position_cylinder_radius * 0.6, height=self.position_cylinder_height * 1.3, resolution=20, split=4)
            self.start_position_cylinder.paint_uniform_color([1.0, 1.0, 1.0])
            self.start_position_cylinder.translate(self.sbet_coordinates[0].np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)

        self.last_extracted_frame_coordinate = None
        self.last_extracted_frame = None
        
        # Initialize the visualizer
        self.initialize_plot_and_visualization()

        if self.preview_always:
            self.vis.refresh_non_blocking()
            self.vis.show_frame(self.full_cloud)
            self.vis.add_geometry(self.actual_position_cylinder)
            self.vis.add_geometry(self.estimated_position_cylinder)
            self.vis.add_geometry(self.start_position_cylinder)

        self.is_first_frame = True

        navigation_exception = None

        # Enumerate all frames until the end of the file and run the merge operation.
        for i in tqdm(range(0, self.frame_limit), total=self.frame_limit, ascii=True, initial=0, **self.tqdm_config):
            
            try:

                if self.merge_next_frame():

                    # Refresh the non-blocking visualization
                    if self.preview_always:
                        self.vis.refresh_non_blocking()
                        self.vis.update_geometry(self.actual_position_cylinder)
                        self.vis.update_geometry(self.estimated_position_cylinder)

                        self.time("visualization refresh")

                        self.check_save_screenshot(i)

                    self.plot.step(self.preview_always)
                    self.time("plot step")

            except Exception as e:

                navigation_exception = e
                
                break

        # When everything is finished, print a summary, and save the point cloud and debug data.
        if self.preview_at_end:
            self.plot.show_plot()
            self.plot.update()

        results = self.check_results_saving(True)
        self.finish_plot_and_visualization()

        if navigation_exception is not None:
            raise navigation_exception

        return results

    def get_current_position(self):

        # Retrieve the index of the currently processed frame
        ix = self.reader.get_current_frame_index()

        # Retrieve the SBET data for this frame, which has
        # already been transformed to fit the point cloud.
        return self.sbet_coordinates[ix]

    def draw_registration_result(self, source, target):
        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        o3d.visualization.draw_geometries([source_temp, target_temp])

    def get_corrected_heading(self, heading):
        heading = heading - np.pi/2
        if heading < 0:
            heading_corrected = np.absolute(heading)
        elif heading > 0:
            heading_corrected = np.pi*2-heading
        return heading_corrected

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

        # Find the current position, and update the blue (actual) position cylinder
        actual_coordinate = self.get_current_position().clone()
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
            self.current_coordinate = actual_coordinate.clone().translate([dx, dy, dz])

        if self.is_first_frame:
            self.is_first_frame = False

        self.time("position extraction")

        # Rotate the frame using the current heading
        #TODO: Should use estimated heading for actual situation!
        R = frame.get_rotation_matrix_from_xyz((0, 0, self.get_corrected_heading(actual_coordinate.heading)))
        frame.rotate(R, center=[0,0,0])

        self.time("frame rotation")

        # Extract a part of the cloud around the actual position. This is the cloud we are going to register against.
        partial_radius = 30
        pr = np.array([partial_radius, partial_radius, partial_radius])

        # Keep a slightly larger partial cloud to make it quicker to extract the actual partial cloud
        # This reduced time usage from 27 to 9 seconds on first 20 frames of a random file.
        c = self.current_coordinate.np()
        if self.last_extracted_frame_coordinate is None or self.last_extracted_frame_coordinate.distance2d(self.current_coordinate) >= partial_radius * 0.8:

            bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=c - pr * 2, max_bound=c + pr * 2)
            self.last_extracted_frame = self.full_cloud.crop(bbox)
            self.last_extracted_frame_coordinate = self.current_coordinate.clone()
           
            self.time("larger partial cloud point extraction")

        bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=c - pr, max_bound=c + pr)
        partial_cloud = self.last_extracted_frame.crop(bbox)

        if len(partial_cloud.points) < 10:
            self.throw_outside_of_cloud(self.current_coordinate, partial_radius)
        
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

        # Run the alignment
        threshold = 2
        reg = self.matcher.match(frame, partial_cloud, threshold)
        while reg.fitness < 0.85 and threshold < 10:
            threshold *= 2
            reg = self.matcher.match(frame, partial_cloud, threshold)
        
        self.registration_configs.append({
            "threshold": threshold, 
            "frame_ix": self.reader.get_current_frame_index(),
            "pcap": self.reader.get_pcap_path()
        })

        self.check_save_frame_pair(partial_cloud, frame, reg)

        registration_time = self.time("registration")

        # Extract the translation part from the transformation array
        movement = reg.transformation[:3,3]

        # Move the estimated position
        self.current_coordinate.translate(movement)
        self.estimated_position_cylinder.translate(self.current_coordinate.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)

        # Append the new movement to the path
        self.movement_path.points.append(self.current_coordinate.np())

        self.update_plot(reg, registration_time, movement, actual_coordinate)

        # Add the new line
        if len(self.movements) == 2:
            if self.preview_always:
                self.vis.add_geometry(self.movement_path)
        if len(self.movements) >= 2:
            self.movement_path.lines.append([len(self.movements) - 2, len(self.movements) - 1])
            self.movement_path.paint_uniform_color([1, 0, 0])
            if self.preview_always:
                self.vis.update_geometry(self.movement_path)

        self.time("book keeping")

        # Update the visualization
        if self.preview_always:
            self.vis.remove_geometry(partial_cloud_visualization)
            self.time("visualization")

        if self.build_cloud:
            transformed_frame = frame.transform(reg.transformation)
            transformed_frame.translate(partial_cloud_transform, relative=True)
            transformed_frame.paint_uniform_color([0,1,0])

            self.add_to_merged_frame(transformed_frame, handle_visualization=True)

            #self.vis.set_follow_vehicle_view(self.current_coordinate.np())

        # Return True to let the loop continue to the next frame.
        return True
        

if __name__ == "__main__":

    parser = NavigatorBase.create_parser()

    parser.add_argument('--point-cloud', type=str, required=True, help="An Open3D point cloud file to use for absolute navigation.")
    
    args = NavigatorBase.add_standard_and_parse_args(parser)

    # Create and start a visualization
    navigator = AbsoluteLidarNavigator(args)
    navigator.print_summary_at_end = True
    navigator.navigate_through_file()