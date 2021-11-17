import open3d as o3d
import numpy as np
from pcapReader import PcapReader

class Open3DVisualizer:

    def __init__(self):
        self._isInitialGeometry = True

        # Create a simple axis visualization
        axes = o3d.geometry.TriangleMesh.create_coordinate_frame(1.0)

        # initialize visualizer and rendering options
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window()
        self.vis.add_geometry(axes)

        ropt = self.vis.get_render_option()
        ropt.point_size = 1.0
        ropt.line_width = 50
        ropt.background_color = np.asarray([0, 0, 0])

        # initialize camera settings
        self.ctr = self.vis.get_view_control()

        self._currentGeometry = None
        self._isNonBlocking = False

    def reset_view(self):
        """Reset the view to the axis center"""
        self.ctr.set_zoom(0.1)
        self.ctr.set_lookat([0, 0, 0])
        self.ctr.set_up([1, 0, 0])
    
    def register_key_callback(self, keyCode, callback):
        self.vis.register_key_callback(keyCode, callback)

    def run(self):
        """Initializes an open3d visualizer"""

        # run visualizer main loop
        print("Press Q or Excape to exit")

        self.vis.run()
        self.vis.destroy_window()

    def refresh_non_blocking(self):
        self.vis.poll_events()
        self.vis.update_renderer()
        self._isNonBlocking = True

    def stop(self):
        self.vis.destroy_window()

    def showFrame(self, frame, removePrevious = False):
        """ Shows the given frame by adding it as a geometry.
        If this is a numpy array, it will be converted to a point cloud.
        """

        if removePrevious and self._currentGeometry is not None:
            self.vis.remove_geometry(self._currentGeometry, False)

        if type(frame) is np.ndarray:
            geometry = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(frame))
        else:
            geometry = frame

        self._currentGeometry = geometry
        self.vis.add_geometry(geometry, self._isInitialGeometry)
        self._isInitialGeometry = False

        if self._isNonBlocking:
            self.vis.update_geometry(geometry)

        return True

    def add_geometry(self, geometry):
        self.vis.add_geometry(geometry, False)

    def update_geometry(self, geometry):
        self.vis.update_geometry(geometry)

    def remove_geometry(self, geometry):
        self.vis.remove_geometry(geometry, False)

    def showFrameFromReader(self, reader:PcapReader, num:int):
        """Show the frame with the given index in the visualizer. This function
        removes the geometry object containing the previous frame, then adds
        the geometry object containing the current frame. If the current frame is
        empty (end of file), this function does nothing, and returns False."""

        frame = reader.readFrame(num)
        if frame is None:
            return False
        
        self.showFrame(frame, True)

        return True