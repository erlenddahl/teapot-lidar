from voxelThinner import VoxelThinner
from voxelThinnerPyoints import VoxelThinnerPyoints
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
        ropt.background_color = np.asarray([0, 0, 0])

        # initialize camera settings
        self.ctr = self.vis.get_view_control()

        self._currentGeometry = None

    def reset_view(self):
        """Reset the view to the axis center"""
        self.ctr.set_zoom(0.1)
        self.ctr.set_lookat([0, 0, 0])
        self.ctr.set_up([1, 0, 0])
    
    def register_key_callback(self, keyCode, callback):
        self.vis.register_key_callback(keyCode, callback)

    def run(self):
        """Initializes an open3d visualizer"""

        self.reset_view()

        # run visualizer main loop
        print("Press Q or Excape to exit")

        self.vis.run()
        self.vis.destroy_window()

    def showFrame(self, frame, removePrevious):

        if removePrevious and self._currentGeometry is not None:
            self.vis.remove_geometry(self._currentGeometry, False)

        geometry = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(frame))
        self._currentGeometry = geometry
        self.vis.add_geometry(geometry, self._isInitialGeometry)
        self._isInitialGeometry = False

        return True