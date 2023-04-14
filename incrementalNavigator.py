from navigatorBase import NavigatorBase
import numpy as np
import os
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
        
        self.initialize_navigation(initial_movement=[[0,0,0]], rotate_sbet=False)

        if self.args.sbet is not None:

            self.current_coordinate = self.sbet_coordinates[0].clone()
            self.initial_coordinate = self.sbet_coordinates[0].clone()

        self.merged_frame = self.reader.next_frame(self.remove_vehicle, self.timer)

        self.previous_frame = self.merged_frame

        # Estimate normals for the first source frame in order to speed up the 
        # alignment operation.
        self.previous_frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        self.initialize_plot_and_visualization()

        self.time("navigation preparations")

        navigation_exception = None

        # Enumerate all frames until the end of the file and run the merge operation.
        for i in tqdm(range(1, self.frame_limit), total=self.frame_limit, initial=1, **self.tqdm_config):
            
            try:

                if self.merge_next_frame(): 

                    # Refresh the non-blocking visualization
                    if self.preview_always:
                        self.vis.refresh_non_blocking()
                        self.vis.set_follow_vehicle_view()
                        self.time("visualization refresh")

                        self.check_save_screenshot(i)

                    self.check_wait()

            except Exception as e:
                
                navigation_exception = e
                
                break

        # Ensure the final cloud has been downsampled
        self.ensure_merged_frame_is_downsampled()

        return self.finalize_navigation(navigation_exception)

    def get_current_position(self, transformed):

        # Retrieve the index of the currently processed frame
        ix = self.reader.get_current_frame_index()

        # Retrieve the SBET data for this frame 
        # This is the original location and time info from the SBET file.
        sbet = self.sbet_coordinates[ix]

        if not transformed:
            return sbet

        # Retrieve the transformed coordinates for this frame from the o3d movement line,
        # which has been transformed after each registration in order to follow the red line.
        o3d = self.actual_movement_path.points[ix]

        # Combine those into one SbetRow with the original Sbet data, but the
        # o3d transformed coordinates.
        pos = sbet.clone()
        pos.x = o3d[0]
        pos.y = o3d[1]
        pos.alt = o3d[2]

        return pos

    def merge_next_frame(self):
        """ Reads the next frame, aligns it with the previous frame, merges them together
        to create a 3D model, and tracks the movement between frames.
        """

        # Fetch the next frame
        frame = self.reader.next_frame(self.remove_vehicle, self.timer)

        self.time("frame extraction")

        # If it is empty, that (usually) means we have reached the end of
        # the file. Return False to stop the loop.
        if frame is None:
            return False
        
        # Retrieve the actual coordinate
        actual_coordinate = self.get_current_position(False) if self.current_coordinate is not None else None

        # Estimate normals for the target frame (the source frame will always have
        # normals from the previous step).
        frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("normal estimation")

        # Run the alignment
        threshold = 1
        reg = self.matcher.match(self.previous_frame, frame, threshold)
        self.registration_configs.append({"threshold": threshold})

        self.check_save_frame_pair(self.previous_frame, frame, reg)

        registration_time = self.time("registration")

        # Calculate how much the center point has moved by transforming [0,0,0] with
        # the calculated transformation
        movement = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(reg.transformation).get_center()

        if self.current_coordinate is not None:
            self.current_coordinate.translate(movement) #TODO: Think this is wrong. Should probably use transformed red line in the end to generate all estimated coordinates.

        self.update_plot(reg, registration_time, movement, actual_coordinate)

        # Append the new movement to the path
        self.movement_path = self.movement_path.transform(reg.transformation)
        self.movement_path.points.append([0,0,0])
        self.movement_path.lines.append([len(self.movement_path.lines), len(self.movement_path.lines) + 1])
        self.movement_path.paint_uniform_color([1, 0, 0])

        # Add the new line
        self.update_live_movement(self.movement_path)

        self.time("book keeping")

        # Transform the frame to fit the merged point cloud
        self.merged_frame = self.merged_frame.transform(reg.transformation)

        self.time("cloud transformation")

        self.add_to_merged_frame(frame)

        # Store this frame so that it can be used as the source frame in the next iteration.
        self.previous_frame = frame

        # Update the visualization
        if self.preview_always:
            self.vis.show_frame(self.merged_frame, True)

            self.time("visualization")

        # Return True to let the loop continue to the next frame.
        return True
        
    def update_live_movement(self, path):
        if not self.preview_always:
            return

        if len(self.movements) == 2:
            self.vis.add_geometry(path)
        if len(self.movements) > 2:
            self.vis.update_geometry(path)

if __name__ == "__main__":

    parser = NavigatorBase.create_parser()
    args = NavigatorBase.add_standard_and_parse_args(parser)

    # Create and start a visualization
    navigator = LidarNavigator(args)
    navigator.print_summary_at_end = True
    navigator.navigate_through_file()