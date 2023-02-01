import open3d as o3d
import numpy as np

class Open3DVisualizer:

    def __init__(self):
        self._is_initial_geometry = True

        self.vis = o3d.visualization.VisualizerWithKeyCallback()

        self._current_geometry = None
        self._is_non_blocking = False

        self.has_been_initialized = False

    def _initialize(self):

        if self.has_been_initialized:
            return

        # Create a simple axis visualization
        axes = o3d.geometry.TriangleMesh.create_coordinate_frame(1.0)

        # initialize visualizer and rendering options
        self.vis.create_window()
        self.vis.add_geometry(axes)

        ropt = self.vis.get_render_option()
        ropt.point_size = 1.0
        ropt.line_width = 50
        ropt.background_color = np.asarray([0, 0, 0])

        # initialize camera settings
        self.ctr = self.vis.get_view_control()

        self.has_been_initialized = True

    def reset_view(self):
        
        self._initialize()

        """Reset the view to the axis center"""
        self.ctr.set_zoom(0.1)
        self.ctr.set_lookat([0, 0, 0])
        self.ctr.set_up([1, 0, 0])

    def set_follow_vehicle_view(self):

        self._initialize()

        """Reset the view to the axis center"""
        self.ctr.set_zoom(0.05)
        self.ctr.set_lookat([0, 0, 0.5])
        self.ctr.set_up([0.35, 0, 0.94])
    
    def register_key_callback(self, key_code, callback):
        self.vis.register_key_callback(key_code, callback)

    def run(self):
        """Initializes an open3d visualizer"""

        self._initialize()

        # run visualizer main loop
        print("Press Q or Excape to exit")

        self.vis.run()
        self.vis.destroy_window()

    def refresh_non_blocking(self):
        
        self._initialize()

        self.vis.poll_events()
        self.vis.update_renderer()
        self._is_non_blocking = True

    def stop(self):
        self.vis.destroy_window()

    def show_frame(self, frame, remove_previous = False):
        """ Shows the given frame by adding it as a geometry.
        If this is a numpy array, it will be converted to a point cloud.
        """

        self._initialize()

        if remove_previous and self._current_geometry is not None:
            self.vis.remove_geometry(self._current_geometry, False)

        if type(frame) is np.ndarray:
            geometry = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(frame))
        else:
            geometry = frame

        self._current_geometry = geometry
        self.vis.add_geometry(geometry, self._is_initial_geometry)
        self._is_initial_geometry = False

        if self._is_non_blocking:
            self.vis.update_geometry(geometry)

        return True

    def add_geometry(self, geometry, reset_bounding_box = False):
        self._initialize()
        self.vis.add_geometry(geometry, reset_bounding_box)

    def update_geometry(self, geometry):
        self._initialize()
        self.vis.update_geometry(geometry)

    def remove_geometry(self, geometry):
        self._initialize()
        self.vis.remove_geometry(geometry, False)

    def capture_screen_image(self, path):
        self.vis.capture_screen_image(path)

    def show_frame_from_reader(self, reader, num):
        """Show the frame with the given index in the visualizer. This function
        removes the geometry object containing the previous frame, then adds
        the geometry object containing the current frame. If the current frame is
        empty (end of file), this function does nothing, and returns False."""

        frame = reader.read_frame(num)
        if frame is None:
            return False
        
        self.show_frame(frame, True)

        return True