from open3dVisualizer import Open3DVisualizer
from navigatorBase import NavigatorBase
from plotter import Plotter
import numpy as np
import os
import copy
from tqdm import tqdm
import open3d as o3d
from datetime import datetime

class LidarNavigator(NavigatorBase):

    def __init__(self, args):
        """Initialize a LidarNavigator by reading metadata and setting
        up a package source from the pcap file.
        """

        NavigatorBase.__init__(self, args)

    def navigate_through_file(self):
        """ Runs through each frame in the file. For each pair of frames, use NICP
        to align the frames, then merge them and downsample the result. The transformation
        matrix from the NICP operation is used to calculate the movement of the center point
        (the vehicle) between the frames. Each movement is stored, and drawn as a red line
        to show the driving route.
        """
        
        self.timer.reset()

        # Initialize the list of movements as well as the merged frame, and the first 
        # source frame.
        self.movements = []
        self.estimated_coordinates = []
        self.actual_coordinates = []
        self.actual_movement_path_transformed = None
        self.total_movement = np.array([0.0,0.0,0.0])

        self.movement_path = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector([]), lines=o3d.utility.Vector2iVector([])
        )

        self.actual_movement_path = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector([]), lines=o3d.utility.Vector2iVector([])
        )

        self.skip_initial_frames()

        self.merged_frame = self.reader.next_frame(self.remove_vehicle, self.timer)

        if args.sbet is not None:
            self.current_coordinate = self.reader.get_current_position().clone()
            self.initial_coordinate = self.current_coordinate.clone()
            print("Initial coordinate:")
            print(self.initial_coordinate)

        self.previous_frame = self.merged_frame

        # Estimate normals for the first source frame in order to speed up the 
        # alignment operation.
        self.previous_frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        # Initialize the visualizer
        self.vis = Open3DVisualizer()

        if self.preview_always:
            # Initiate non-blocking visualizer window
            self.vis.refresh_non_blocking()

            # Show the first frame and reset the view
            self.vis.show_frame(self.merged_frame)
            self.vis.set_follow_vehicle_view()

            self.check_save_screenshot(0, True)

        plot = Plotter(self.preview_always)

        self.time("navigation preparations")

        # Enumerate all frames until the end of the file and run the merge operation.
        for i in tqdm(range(1, self.frame_limit), total=self.frame_limit, ascii=True, initial=1, **self.tqdm_config):
            
            try:

                if self.merge_next_frame(plot): 

                    # Refresh the non-blocking visualization
                    if self.preview_always:
                        self.vis.refresh_non_blocking()
                        self.vis.set_follow_vehicle_view()
                        self.time("visualization refresh")

                        self.check_save_screenshot(i)

                    plot.step(self.preview_always)
                    self.time("plot step")

            except KeyboardInterrupt:
                
                print("")
                print("********************************")
                print("Process aborted. Results so far:")
                print("********************************")
                plot.print_summary(self.timer)
                print("")
                print("")

                raise

        # Ensure the final cloud has been downsampled
        self.ensure_merged_frame_is_downsampled()

        # When everything is finished, print a summary, and save the point cloud and debug data.
        if self.preview_at_end:
            plot.update()

        results = self.get_results(plot)
        
        results["estimated_coordinates"] = [x.json() for x in self.estimated_coordinates]
        results["actual_coordinates"] = [x.json(True) for x in self.actual_coordinates]

        if self.save_path is not None:
            filenameBase = self.save_path.replace("[time]", datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f%z'))
            filenameBase = filenameBase.replace("[pcap]", os.path.basename(self.reader.pcap_path).replace(".pcap", ""))

            self.ensure_dir(os.path.join(filenameBase, "plot.png"))
            plot.save_plot(os.path.join(filenameBase, "plot.png"))

            if self.build_cloud:
                self.save_cloud_as_las(os.path.join(filenameBase, "cloud.laz"), self.merged_frame)
                o3d.io.write_point_cloud(os.path.join(filenameBase, "cloud.pcd"), self.merged_frame, compressed=True)

            self.time("results saving")
            
            self.save_data(os.path.join(filenameBase, "data.json"), results)
        
        if self.print_summary_at_end:
            plot.print_summary(self.timer)

        # Then continue showing the visualization in a blocking way until the user stops it.
        if self.preview_at_end:
            self.vis.show_frame(self.merged_frame)

            self.vis.remove_geometry(self.movement_path)
            self.vis.add_geometry(self.movement_path)

            self.vis.remove_geometry(self.actual_movement_path_transformed)
            self.vis.add_geometry(self.actual_movement_path_transformed)

            self.vis.reset_view()

            self.vis.run()

        plot.destroy()

        return results

    def update_plot(self, plot, reg, registration_time, movement, actual_coordinate):
        plot.timeUsages.append(registration_time)
        plot.rmses.append(reg.inlier_rmse)
        plot.fitnesses.append(reg.fitness)
        plot.distances.append(np.sqrt(np.dot(movement, movement)))
        
        if self.current_coordinate is not None:

            self.actual_coordinates.append(actual_coordinate)
            self.estimated_coordinates.append(self.current_coordinate.clone())

            self.current_coordinate.x += movement[0]
            self.current_coordinate.y += movement[1]
            self.current_coordinate.alt += movement[2]

            dx = actual_coordinate.x - self.current_coordinate.x
            dy = actual_coordinate.y - self.current_coordinate.y
            dz = actual_coordinate.alt - self.current_coordinate.alt

            plot.position_error_x.append(dx)
            plot.position_error_y.append(dy)
            plot.position_error_z.append(dz)
            plot.position_error_2d.append(np.sqrt(dx*dx+dy*dy))
            plot.position_error_3d.append(np.sqrt(dx*dx+dy*dy+dz*dz))
            plot.position_age.append(actual_coordinate.age)

    def merge_next_frame(self, plot):
        """ Reads the next frame, aligns it with the previous frame, merges them together
        to create a 3D model, and tracks the movement between frames.
        """

        # Fetch the next frame
        frame = self.reader.next_frame(self.remove_vehicle, self.timer)

        # If it is empty, that (usually) means we have reached the end of
        # the file. Return False to stop the loop.
        if frame is None:
            return False

        # Estimate normals for the target frame (the source frame will always have
        # normals from the previous step).
        frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("normal estimation")

        # Run the alignment
        reg = self.matcher.match(self.previous_frame, frame)
        self.check_save_frame_pair(self.previous_frame, frame, reg)

        registration_time = self.time("registration")

        # Extract the movement (translation) from the transformation
        movement = reg.transformation[:3,3]
        self.total_movement += movement
        
        actual_coordinate = self.reader.get_current_position() if self.current_coordinate is not None else None
        self.update_plot(plot, reg, registration_time, movement, actual_coordinate)

        # Append the newest movement
        self.movements.append(movement)

        # Append the new movement to the path
        self.movement_path.points.append([0,0,0])
        self.movement_path = self.movement_path.transform(reg.transformation)

        # Add the new line
        if len(self.movements) == 2:
            self.vis.add_geometry(self.movement_path)
        if len(self.movements) >= 2:
            self.movement_path.lines.append([len(self.movements) - 2, len(self.movements) - 1])
            self.movement_path.paint_uniform_color([1, 0, 0])
            self.vis.update_geometry(self.movement_path)

        if self.actual_movement_path is not None:

            self.actual_movement_path.points.append([actual_coordinate.x, actual_coordinate.y, actual_coordinate.alt])
            if len(self.actual_movement_path.points) >= 2:
                self.actual_movement_path.lines.append([len(self.actual_movement_path.points) - 2, len(self.actual_movement_path.points) - 1])
            self.actual_movement_path.paint_uniform_color([0, 0, 1])

            if self.actual_movement_path_transformed is not None:
                self.vis.remove_geometry(self.actual_movement_path_transformed)
            self.actual_movement_path_transformed = copy.deepcopy(self.actual_movement_path)

            fp = self.movement_path.points[0]
            self.actual_movement_path_transformed.translate((fp[0] - self.initial_coordinate.x, fp[1] - self.initial_coordinate.y, fp[2] - self.initial_coordinate.alt))
            R = self.actual_movement_path_transformed.get_rotation_matrix_from_xyz((0, 0, 1.8611953258514404))
            self.actual_movement_path_transformed.rotate(R, center=(fp[0], fp[1], fp[2]))
            
            # Add the actual coordinate as a blue line
            if len(self.actual_movement_path.points) == 2:
                self.vis.add_geometry(self.actual_movement_path_transformed)
            if len(self.actual_movement_path.points) > 2:
                self.vis.add_geometry(self.actual_movement_path_transformed)
            


        self.time("book keeping")

        # Transform the frame to fit the merged point cloud
        self.merged_frame = self.merged_frame.transform(reg.transformation)

        # Add the frame to the generated point cloud (unless we should skip some frames)
        self.build_cloud_timer -= 1
        if self.build_cloud and self.build_cloud_timer <= 0:

            self.time("frame transformation")

            # Combine the points from the merged visualization with the points from the next frame
            self.merged_frame += frame
            self.merged_frame_is_dirty = True
            self.build_cloud_timer = self.build_cloud_after

            self.time("cloud merging")

            # Downsample the merged visualization to make it faster to work with.
            # Otherwise it would grow extremely large, as it would contain all points
            # from all processed point clouds.
            # Don't do this on every frame, as it takes a lot of time.
            self.downsample_timer -= 1
            if self.downsample_timer <= 0:
                self.ensure_merged_frame_is_downsampled()
                self.downsample_timer = self.downsample_cloud_after_frames

        # Store this frame so that it can be used as the source frame in the next iteration.
        self.previous_frame = frame

        # Update the visualization
        if self.preview_always:
            self.vis.show_frame(self.merged_frame, True)

            self.time("visualization")

        # Return True to let the loop continue to the next frame.
        return True
        

if __name__ == "__main__":

    parser = NavigatorBase.create_parser()
    args = NavigatorBase.add_standard_and_parse_args(parser)

    # Create and start a visualization
    navigator = LidarNavigator(args)
    navigator.print_summary_at_end = True
    navigator.navigate_through_file()