from navigatorBase import NavigatorBase
import numpy as np
import os
from tqdm import tqdm
import open3d as o3d
import copy
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
        
        self.initialize_navigation(rotate_sbet=False)        
        self.initialize_plot_and_visualization()

        frame = self.reader.next_frame(self.remove_vehicle, self.timer)
        self.rotate_frame(frame, self.get_current_actual_coordinate())
        self.transform_and_add_to_merged_frame(frame)
        self.previous_frame = frame

        # Estimate normals for the first source frame in order to speed up the 
        # alignment operation.
        self.previous_frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("navigation preparations")

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

        if self.run_until_ix > 0 and self.reader.get_current_frame_index() >= self.run_until_ix:
            return False

        # Estimate normals for the target frame (the source frame will always have
        # normals from the previous step).
        frame.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        self.time("normal estimation")
        
        # Retrieve the actual coordinate
        actual_coordinate = self.get_current_actual_coordinate().clone()
        self.actual_position_cylinder.translate(actual_coordinate.np() + np.array([0, 0, self.position_cylinder_height / 2]), relative=False)

        # Run the alignment
        reg = self.run_registration(frame, self.previous_frame, actual_coordinate)

        self.transform_and_add_to_merged_frame(frame, reg)

        # Store this frame so that it can be used as the source frame in the next iteration.
        self.previous_frame = frame

        # Return True to let the loop continue to the next frame.
        return True

    def transform_and_add_to_merged_frame(self, frame, reg=None):
        transformed_frame = copy.deepcopy(frame)
        if reg is not None:
            transformed_frame.transform(reg.transformation)
        transformed_frame.translate(self.current_estimated_coordinate.np())
        self.add_to_merged_frame(transformed_frame, True)

if __name__ == "__main__":

    parser = NavigatorBase.create_parser()
    args = NavigatorBase.add_standard_and_parse_args(parser)

    # Create and start a visualization
    navigator = LidarNavigator(args)
    navigator.print_summary_at_end = True
    navigator.navigate_through_file()