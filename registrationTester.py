import os
import copy
import json
import time
import shutil
import argparse
import numpy as np
import open3d as o3d
from tqdm import tqdm

from matchers.nicp import NicpMatcher
from matchers.downsamplefirst import DownsampleFirstNicpMatcher
from matchers.globalregistrationfirst import GlobalFirstNicpMatcher
from matchers.fastglobalregistrationfirst import FastGlobalFirstNicpMatcher

class RegistrationTester:

    def __init__(self, dataset_path, results_name):
        
        self.dataset_path = dataset_path
        self.results_name = results_name
        self.path_results = os.path.join(dataset_path, results_name)
        self.path_summary_json = os.path.join(dataset_path, results_name + ".json")
        self.path_summary_md = os.path.join(dataset_path, results_name + ".md")

        self.init_algorithms()

    def init_algorithms(self):

        self.algorithms = []

        self.add_algorithm(NicpMatcher(), "NICP")
        self.add_algorithm(DownsampleFirstNicpMatcher(), "Downsample (0.5), then NICP")
        self.add_algorithm(DownsampleFirstNicpMatcher(0.1), "Downsample (0.1), then NICP")
        self.add_algorithm(DownsampleFirstNicpMatcher(0.05), "Downsample (0.05), then NICP")
        self.add_algorithm(GlobalFirstNicpMatcher(), "Global registration, then NICP")
        self.add_algorithm(FastGlobalFirstNicpMatcher(), "Fast global registration, then NICP")

    def add_algorithm(self, algo, name):
        algo.name = name
        self.algorithms.append(algo)

    def clean(self):
        if os.path.isfile(self.path_summary_md):
            os.remove(self.path_summary_md)
        if os.path.isfile(self.path_summary_json):
            os.remove(self.path_summary_json)
        if os.path.isdir(self.path_results):
            shutil.rmtree(self.path_results)

    def run(self):

        summary = {}
        if os.path.isfile(self.path_summary_json):
            try:
                with open(self.path_summary_json, 'r') as file:
                    summary = json.load(file)
            except:
                pass # If error, skip JSON loading
        
        datasets = [x for x in os.listdir(self.dataset_path) if os.path.isdir(os.path.join(self.dataset_path, x))]

        for dataset in tqdm(datasets, desc="Datasets", position=0, ascii=True):
            for algorithm in tqdm(self.algorithms, desc="Algorithms", position=1, ascii=True, leave=False):

                key = dataset + "_" + algorithm.name

                if key in summary:
                    continue

                if dataset.startswith("pairs_"):
                    summary[key] = self.run_pairs(key, dataset, algorithm)
                else:
                    raise ValueError("Invalid dataset type: " + dataset)

                with open(self.path_summary_json, 'w') as file:
                    json.dump(summary, file)

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
        for key in tqdm(groups, desc="Pairs", position=2, ascii=True, leave=False):

            # We repeat the reading for every algorithm in case any of them should ever change anything in the clouds.
            source = o3d.io.read_point_cloud(os.path.join(dataset_path, groups[key][0]))
            target = o3d.io.read_point_cloud(os.path.join(dataset_path, groups[key][1]))

            start_time = time.perf_counter()
            results[key] = self.create_result(algorithm.match(source, target), result_key + "_" + key, source, target, start_time)

        return results

    def create_result(self, result, key, source, target, start_time):

        time_usage = time.perf_counter() - start_time
        image_path = os.path.join(self.path_results, "screenshots", key + ".png")
        
        self.save_screenshot(source, source.transform(result.transformation), target, image_path)

        movement = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray([[0.0,0.0,0.0]]))).transform(result.transformation).get_center()
        
        return {
            "time_usage": time_usage,
            "rmse": result.inlier_rmse,
            "fitness": result.fitness,
            "movement_distance": np.sqrt(np.dot(movement, movement)),
            "image": image_path,
            "transformation": list(movement)
        }

    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if len(directory) < 1: 
            return
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_screenshot(self, source, transformed_source, target, path):
        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False) # May be set to True on some systems

        ropt = vis.get_render_option()
        ropt.point_size = 1.0
        ropt.background_color = np.asarray([0, 0, 0])

        source_temp = copy.deepcopy(source)
        transformed_source_temp = copy.deepcopy(transformed_source)
        target_temp = copy.deepcopy(target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        transformed_source_temp.paint_uniform_color([1/2.0, 0.706/2.0, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])

        for g in [source_temp, transformed_source_temp, target_temp]:
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
    parser.add_argument('--datasets', type=str, required=True, help="The path to a directory containing one or more dataset directories. Results will be saved in the same directory.")
    parser.add_argument('--results-name', type=str, default='results', help="The name of the results file and folder.")
    parser.add_argument('--clean', dest='clean', action='store_true', help="If set, all previous results will be deleted before running (otherwise, algorithms and datasets with previous results will be skipped).")

    args = parser.parse_args()

    navigator = RegistrationTester(args.datasets, args.results_name)

    if args.clean:
        navigator.clean()

    navigator.run()