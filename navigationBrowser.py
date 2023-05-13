from navigatorBase import NavigatorBase
from utils.open3dVisualizer import Open3DVisualizer
import numpy as np
import os
from tqdm import tqdm
import open3d as o3d
from datetime import datetime
import copy
import json
from absoluteNavigator import AbsoluteLidarNavigator

class NavigationBrowser(AbsoluteLidarNavigator):

    def __init__(self, args):
        """Initialize an AbsoluteLidarNavigator by reading metadata and setting
        up a package source from the pcap file.
        """

        AbsoluteLidarNavigator.__init__(self, args)
        self.initialize_navigation(rotate_sbet=False)
        self.vis = Open3DVisualizer()
        self.vis.add_geometry(self.full_cloud)
        self.vis.add_geometry(self.actual_movement_path)
        self.shown_frame = None
        self.heading_offset = 0

        self.next_frame(True)

    def next_frame(self, is_first=False):

        frame = self.reader.next_frame(False, self.timer, False)
        
        if frame is None:
            print("Empty frame -- probably end of file.")
            return

        self.set_frame(frame, is_first)

    def set_frame(self, frame, is_first=False):
        
        self.read_frame = copy.deepcopy(frame)

        coordinate = self.get_current_actual_coordinate()

        print("")
        print("Index offset:", self.frame_index_offset)
        print(f"Heading offset: {self.heading_offset/100.0:.2f}")
        print(coordinate)

        R = frame.get_rotation_matrix_from_xyz((coordinate.roll, coordinate.pitch, self.get_corrected_heading(coordinate.heading + self.heading_offset / 100.0)))
        frame.rotate(R, center=[0,0,0])

        frame.translate(coordinate.np(), relative=True)

        if self.shown_frame is not None:
            self.vis.remove_geometry(self.shown_frame)

        self.vis.add_geometry(frame, is_first)
        self.shown_frame = frame

    def start(self):
    
        def key_n(vis):
            self.next_frame()
    
        def key_left(vis):
            self.heading_offset += 1
            self.set_frame(self.read_frame)
    
        def key_right(vis):
            self.heading_offset -= 1
            self.set_frame(self.read_frame)
    
        def key_up(vis):
            self.frame_index_offset += 1
            self.set_frame(self.read_frame)
    
        def key_down(vis):
            self.frame_index_offset -= 1
            self.set_frame(self.read_frame)

        self.vis.register_key_callback(78, key_n)
        self.vis.register_key_callback(262, key_right)
        self.vis.register_key_callback(263, key_left)
        self.vis.register_key_callback(264, key_down)
        self.vis.register_key_callback(265, key_up)
        # List of key codes can be found here: https://www.glfw.org/docs/latest/group__keys.html

        self.vis.reset_view()
        self.vis.run()

if __name__ == "__main__":

    browser = NavigationBrowser(AbsoluteLidarNavigator.read_args())
    browser.start()