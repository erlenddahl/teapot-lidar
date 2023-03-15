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

        self.print_cloud_info("Cloud", self.full_cloud, "    ")
        
        self.full_cloud.paint_uniform_color([0.3, 0.6, 1.0])
        self.full_cloud_np = np.asarray(self.full_cloud.points)

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
            self.actual_coordinates = self.reader.get_coordinates(False, show_progress=True)

            # Translate all coordinates towards origo with the same offset as
            # the point cloud.
            for c in self.actual_coordinates:
                c.translate(self.full_point_cloud_offset)
            
            self.current_coordinate = self.actual_coordinates[0].clone()
            self.initial_coordinate = self.actual_coordinates[0].clone()

            self.actual_movement_path = o3d.geometry.LineSet(
                points = o3d.utility.Vector3dVector([[p.x, p.y, p.alt] for p in self.actual_coordinates]), 
                lines = o3d.utility.Vector2iVector([[i, i+1] for i in range(len(self.actual_coordinates) - 1)])
            )
            self.actual_movement_path.paint_uniform_color([0, 0, 1])
            
            self.actual_position_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=self.position_cylinder_radius, height=self.position_cylinder_height, resolution=20, split=4)
            self.actual_position_cylinder.paint_uniform_color([0.0, 0.0, 1.0])
            
            self.estimated_position_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=self.position_cylinder_radius, height=self.position_cylinder_height, resolution=20, split=4)
            self.estimated_position_cylinder.paint_uniform_color([1.0, 0.0, 0.0])
        
        # Initialize the visualizer
        self.initialize_plot_and_visualization()        
        
        self.is_first_frame = True

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

            except KeyboardInterrupt:
                
                print("")
                print("********************************")
                print("Process aborted. Results so far:")
                print("********************************")
                self.plot.print_summary(self.timer)
                print("")
                print("")

                raise

        # When everything is finished, print a summary, and save the point cloud and debug data.
        if self.preview_at_end:
            self.plot.show_plot()
            self.plot.update()

        self.print_cloud_info("Full cloud", self.full_cloud)

        self.check_results_saving(True)
        self.finish_plot_and_visualization()

        return results

    def get_current_position(self):

        # Retrieve the index of the currently processed frame
        ix = self.reader.get_current_frame_index()

        # Retrieve the SBET data for this frame, which has
        # already been transformed to fit the point cloud.
        return self.actual_coordinates[ix]

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

    def merge_next_frame(self):
        """ Reads the next frame, aligns it with the previous frame, merges them together
        to create a 3D model, and tracks the movement between frames.
        """

        # Find the current position, and update the blue (actual) position cylinder
        actual_position = self.get_current_position().clone()
        self.actual_position_cylinder.translate(actual_position.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)

        self.estimated_position_cylinder.translate(actual_position.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)
        if self.is_first_frame:
            self.is_first_frame = False

        self.time("position extraction")

        # Fetch the next frame
        frame = self.reader.next_frame(self.remove_vehicle, self.timer, False)

        # Rotate the frame using the current heading
        #TODO: Should use estimated heading for actual situation!
        R = frame.get_rotation_matrix_from_xyz((0, 0, self.get_corrected_heading(actual_position.heading)))
        frame.rotate(R, center=[0,0,0])

        self.time("frame extraction")

        # Extract a part of the cloud around the actual position. This is the cloud we are going to register against.
        a = self.full_cloud_np
        partial_radius = 50
        points = a[(a[:, 0] >= actual_position.x - partial_radius) & (a[:, 0] <= actual_position.x + partial_radius) & (a[:, 1] >= actual_position.y - partial_radius) & (a[:, 1] <= actual_position.y + partial_radius)]
        if len(points) < 10:
            print("")
            print("")
            self.print_cloud_info("Cloud", self.full_cloud, "    ")
            print("Current position:", actual_position)
            print("Radius:", partial_radius)
            raise Exception("The point cloud contains no points around the current position.")
        self.time("partial cloud point extraction")

        # Move the points so that the actual coordinate is in the origin.
        # Now, both the current frame and this part of the cloud should be positioned very close to each other around the origin.
        points -= np.array([actual_position.x, actual_position.y, actual_position.alt])
        self.time("partial cloud point movement")

        # Create an o3d point cloud object from the points
        partial_cloud = o3d.geometry.PointCloud()
        partial_cloud.points = o3d.utility.Vector3dVector(points)
        self.time("partial cloud creation")

        # If it is empty, that (usually) means we have reached the end of
        # the file. Return False to stop the loop.
        if frame is None:
            return False

        # Estimate normals for the target frame
        frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("frame normal estimation")

        # For now, estimate normals for the partial cloud as well (to save some time, try to transfer them from the full cloud!)
        partial_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("partial cloud normal estimation")

        # Run the alignment
        reg = self.matcher.match(frame, partial_cloud, 10, None)
        self.check_save_frame_pair(partial_cloud, frame, reg)

        registration_time = self.time("registration")

        # Extract the translation part from the transformation array
        movement = reg.transformation[:3,3]
        
        self.plot.timeUsages.append(registration_time)
        self.plot.rmses.append(reg.inlier_rmse)
        self.plot.fitnesses.append(reg.fitness)
        self.plot.distances.append(np.sqrt(np.dot(movement, movement)))

        # Append the newest movement
        self.movements.append(movement)

        # Append the new movement to the path
        self.movement_path.points.append(reg.transformation[:3,3])

        self.estimated_position_cylinder.transform(reg.transformation)

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

        self.previous_transformation = reg.transformation

        # Combine the points from the merged visualization with the points from the next frame
        transformed_frame = copy.deepcopy(frame)
        print("Movement", movement)
        print("Transformation:")
        print(reg.transformation)
        transformed_frame.transform(reg.transformation)

        # Update the visualization
        if self.preview_always and self.vis is not None:
            # TODO: cylinder stuff
            self.time("visualization")

        # The following lines are a temporary debugging visualization

        partial_cloud.paint_uniform_color([1,0,0])
        frame.paint_uniform_color([0,1,0])
        transformed_frame.paint_uniform_color([0,0,1])

        self.print_cloud_info("Full cloud (bright blue)", self.full_cloud)
        self.print_cloud_info("Partial cloud (red)", partial_cloud)
        self.print_cloud_info("Current frame (green)", frame)
        self.print_cloud_info("Transformed frame (blue)", transformed_frame)

        vis = Open3DVisualizer()
        vis.show_frame(self.full_cloud)
        vis.add_geometry(self.actual_movement_path)
        vis.add_geometry(partial_cloud)
        vis.add_geometry(frame)
        vis.add_geometry(transformed_frame)
        vis.add_geometry(self.actual_position_cylinder)
        vis.add_geometry(self.estimated_position_cylinder)
        vis.reset_view()
        vis.run()
        afdsajhuiCRASH

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