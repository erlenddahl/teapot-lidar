from utils.open3dVisualizer import Open3DVisualizer
import numpy as np
from tqdm import tqdm
from datetime import datetime
import open3d as o3d
import csv
from sbet.sbetParser import SbetParser
from pcap.pcapReaderHelper import PcapReaderHelper

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    PcapReaderHelper.add_sbet_arguments(parser)
    parser.add_argument('--gps-week', type=int, default=-1, required=False, help="If given, this GPS week will be used to transform the timestamps to unix and human readable time.")
    parser.add_argument('--gps-epoch', type=int, default=-1, required=False, help="If given, this GPS epoch will be used to transform the coordinates.")
    parser.add_argument('--out-csv', type=str, required=False, help="If given, coordinates will be saved to this CSV file instead of being visualized.")
    args = parser.parse_args()

    # Create and start a visualization
    parser = SbetParser(args.sbet, args.sbet_noise, args.sbet_noise_from_frame_ix, args.sbet_crs_from, args.sbet_crs_to)
    parser.gps_epoch = args.gps_epoch
    
    min_time = np.min(parser.rows["time"])
    max_time = np.max(parser.rows["time"])

    print("From CRS:", parser.crs_from)
    print("To CRS:", parser.crs_to)
    print("To CRS:", parser.gps_epoch)

    print("Min time:", min_time)
    print("Max time:", max_time)

    if args.gps_week >= 0:

        print("With GPS week:", args.gps_week)
        
        min_unix_time = timestamp_sow2unix(min_time, args.gps_week)
        max_unix_time = timestamp_sow2unix(max_time, args.gps_week)
        print("Min unix time:", min_unix_time)
        print("Max unix time:", max_unix_time)
        
        print("Min human time:", datetime.utcfromtimestamp(min_unix_time).strftime("%Y-%m-%d %H:%M:%S"))
        print("Max human time:", datetime.utcfromtimestamp(max_unix_time).strftime("%Y-%m-%d %H:%M:%S"))

    print("Min lat:", np.min(parser.rows["lat"]))
    print("Max lat:", np.max(parser.rows["lat"]))
    
    print("Min lon:", np.min(parser.rows["lon"]))
    print("Max lon:", np.max(parser.rows["lon"]))

    print("Initial heading:", parser.rows[0]["heading"])

    print("First row:", parser.rows[0])

    coords = parser.get_rows()

    print("First coordinate:", coords[0])

    if args.out_csv is not None:

        with open(args.out_csv, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(coords[0].get_csv_headers())
            for c in coords:
                writer.writerow(c.get_csv())

    else:

        path = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector([[p.x, p.y, p.alt] for p in coords]), lines=o3d.utility.Vector2iVector([[i, i+1] for i in range(len(coords) - 1)])
        )
        path.paint_uniform_color([1, 0, 0])
        
        coords = parser.get_rows(rotate=True)
        transformed_path = o3d.geometry.LineSet(
            points = o3d.utility.Vector3dVector([[p.x, p.y, p.alt] for p in coords]), lines=o3d.utility.Vector2iVector([[i, i+1] for i in range(len(coords) - 1)])
        )
        transformed_path.paint_uniform_color([0, 0, 1])

        position_cylinder_radius = 1
        position_cylinder_height = 20
        actual_position_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=position_cylinder_radius, height=position_cylinder_height, resolution=20, split=4)
        actual_position_cylinder.paint_uniform_color([0, 0, 1])

        vis = Open3DVisualizer()
        vis.add_axes = False
        vis.show_frame(transformed_path)
        vis.add_geometry(path)
        vis.add_geometry(actual_position_cylinder)

        for c in tqdm(coords, ascii=True, desc="Animating"):
            actual_position_cylinder.translate(c.np() + np.array([0, 0, position_cylinder_height / 2]), relative=False)
            vis.update_geometry(actual_position_cylinder)
            vis.refresh_non_blocking()

        vis.run()