import os
import copy
import json
import time
import shutil
import argparse
import numpy as np
import open3d as o3d
from tqdm import tqdm
from algorithmHelper import AlgorithmHelper

from navigator import LidarNavigator

class RegistrationTester:

    def __init__(self, config_file):
        
        self.config_file = config_file
        self.dataset_path = os.path.dirname(config_file)
        results_name = os.path.basename(config_file).lower().replace(".json", "")
        self.path_results = os.path.join(self.dataset_path, "results", results_name)
        self.path_summary_json = os.path.join(self.path_results, "summary.json")

        self.algorithms = AlgorithmHelper.get_all_algorithms()

        with open(config_file, 'r') as file:
            self.config = json.load(file)

    def clean(self):
        if os.path.isdir(self.path_results):
            shutil.rmtree(self.path_results)

    def run(self):

        summary = {}
        if os.path.isfile(self.path_summary_json):
            try:
                with open(self.path_summary_json, 'r') as file:
                    summary = json.load(file)
            except Exception as e:
                print("Failed to read JSON:", e)
                pass # If error, skip JSON loading

        datasets = self.config["datasets"]
        algorithms = [x for x in self.algorithms if x.name in self.config["algorithms"]]

        for dataset in tqdm(datasets, desc="Datasets", position=0, ascii=True):
            for algorithm in tqdm(algorithms, desc="Algorithms", position=1, ascii=True, leave=False):
                for run in tqdm(self.config["runs"], desc="Runs", position=2, ascii=True, leave=False):

                    key = [dataset, algorithm.name, run["id"]]
                    key_string = "_".join(key)

                    if key_string in summary:
                        continue

                    if dataset.startswith("pairs_"):
                        summary[key_string] = self.run_pairs(key, dataset, algorithm)
                    elif dataset.startswith("pcap_"):
                        summary[key_string] = self.run_pcaps(key, run, dataset, algorithm)
                    else:
                        raise ValueError("Invalid dataset type: " + dataset)

                    self.save_summary(summary)

    def save_summary(self, summary):
        with open(self.path_summary_json, 'w') as file:
            json.dump(summary, file, indent=4)

    def run_pcaps(self, result_key, run, dataset, algorithm):

        dataset_path = os.path.join(self.dataset_path, dataset)
        
        results_path = os.path.join(self.path_results, "pcap_results", "_".join(result_key))
        navigator = LidarNavigator(dataset_path, preview="never", save_path=results_path)

        navigator.matcher = algorithm
        navigator.remove_vehicle = run["remove_vehicle"]

        if "max_distance" in run:
            navigator.reader.max_distance = run["max_distance"]

        navigator.tqdm_config = {
            "position": 3,
            "leave": False
        }

        results = navigator.navigate_through_file()

        # Remove stuff that is stored in the results file anyway
        del results["fitnesses"]
        del results["distances"]
        del results["timeUsages"]
        del results["rmses"]
        del results["movement"]

        results["results"] = results_path
        results["pcap-run"] = run

        return results


    def run_pairs(self, result_key, dataset, algorithm):

        dataset_path = os.path.join(self.dataset_path, dataset)
        files = [x.lower() for x in os.listdir(dataset_path) if os.path.isfile(os.path.join(dataset_path, x)) and x.lower().endswith(".pcd")]
        groups = {}

        for file in files:
            group = file.replace("_a.pcd", "").replace("_b.pcd", "")

            if group in groups:
                groups[group].append(file)
            else:
                groups[group] = [file]

        results = {}
        for key in tqdm(groups, desc="Pairs", position=3, ascii=True, leave=False):

            # We repeat the reading for every algorithm in case any of them should ever change anything in the clouds.
            source = o3d.io.read_point_cloud(os.path.join(dataset_path, groups[key][0]))
            target = o3d.io.read_point_cloud(os.path.join(dataset_path, groups[key][1]))

            start_time = time.perf_counter()
            results[key] = self.create_result(algorithm.match(source, target), result_key + [key], source, target, start_time)

        return results

    def create_result(self, result, key, source, target, start_time):

        time_usage = time.perf_counter() - start_time
        image_path_before = os.path.join(self.path_results, "screenshots", "before_" + key[0] + "_" + key[2] + ".png")
        image_path_after = os.path.join(self.path_results, "screenshots", "_".join(key) + "_after.png")
        
        if not os.path.isfile(image_path_before):
            self.save_screenshot(source, target, image_path_before)
        self.save_screenshot(source.transform(result.transformation), target, image_path_after)

        movement = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(result.transformation).get_center()
        
        return {
            "time_usage": time_usage,
            "rmse": result.inlier_rmse,
            "fitness": result.fitness,
            "movement_distance": np.sqrt(np.dot(movement, movement)),
            "image_before": image_path_before,
            "image_after": image_path_after,
            "transformation": list(movement)
        }

    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if len(directory) < 1: 
            return
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_screenshot(self, source, target, path):
        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False) # May be set to True on some systems

        ropt = vis.get_render_option()
        ropt.point_size = 1.0
        ropt.background_color = np.asarray([0, 0, 0])

        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])

        for g in [source_temp, target_temp]:
            vis.add_geometry(g)
            vis.update_geometry(g)

        ctr = vis.get_view_control()
        ctr.set_zoom(0.1)
        ctr.set_lookat([0, 0, 0])
        ctr.set_up([0.85, 0.12, 0.52])
        
        vis.poll_events()
        vis.update_renderer()
        
        self.ensure_dir(path)
        vis.capture_screen_image(path)

        vis.destroy_window()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=str, required=True, help="The path to a test config file.")
    parser.add_argument('--clean', dest='clean', action='store_true', help="If set, all previous results will be deleted before running (otherwise, runs with previous results will be skipped).")

    args = parser.parse_args()

    navigator = RegistrationTester(args.run)

    if args.clean:
        navigator.clean()

    navigator.run()