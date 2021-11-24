import matplotlib.pyplot as plt
from tabulate import tabulate
import math
import statistics

class Plotter:

    def __init__(self, showPlot = True):

        # Initialize plot
        self.plot_x = []

        self.fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False)
        self.axes = [ax1, ax2, ax3]

        # Initialize value arrays
        self.distances = []
        self.timeUsages = []
        self.rmses = []
        self.fitnesses = []

    def step(self, updatePlot = True):
        self.plot_x.append(len(self.distances) - 1)

        if updatePlot:
            self.update()

    def update(self):
        
        # Enable interactive mode, which redraws plot on change
        plt.ion()
        # Show the plot without blocking
        plt.show(block=False)

        (ax1, ax2, ax3) = self.axes

        ax1.clear()
        ax2.clear()
        ax3.clear()

        ax1.plot(self.plot_x, self.timeUsages, color="blue", label="calculation time")
        ax2.plot(self.plot_x, self.distances, color="red", label="distance")
        ax3.plot(self.plot_x, self.rmses, color="purple", label="rmse")
        ax3.plot(self.plot_x, self.fitnesses, color="green", label="fitness")
        
        ax1.set_ylabel("Seconds")
        ax2.set_ylabel("Meters")
        ax3.set_xlabel("Frame index")

        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        handles3, labels3 = ax3.get_legend_handles_labels()
        self.fig.legend(handles1+handles2+handles3, labels1+labels2+labels3, loc='center right')

    def print_summary(self, timer = None):

        print(tabulate(self.get_summary(timer)))

    def get_summary(self, timer = None):

        nonPerfect = [x for x in self.fitnesses if x <= 0.95]

        lines = [
            ["Number of frames:", len(self.plot_x) + 1],
            ["Total movement distance:", sum(self.distances)],
            ["Max distance: ", max(self.distances)],
            ["Avg distance: ", statistics.mean(self.distances)],
            ["Min distance: ", min(self.distances)],
            ["Total registration time usage: ", sum(self.timeUsages)],
            ["Max time: ", max(self.timeUsages)],
            ["Avg time: ", statistics.mean(self.timeUsages)],
            ["Min time: ", min(self.timeUsages)],
            ["Max fitness: ", max(self.fitnesses)],
            ["Avg fitness: ", statistics.mean(self.fitnesses)],
            ["Avg non-perfect fitness: ", statistics.mean(nonPerfect) if len(nonPerfect) > 0 else "-"],
            ["Min fitness: ", min(self.fitnesses)],
            ["Max rmse: ", max(self.rmses)],
            ["Avg rmse: ", statistics.mean(self.rmses)],
            ["Min rmse: ", min(self.rmses)]
        ]

        if timer is not None:
            for key in timer.timings:
                lines.append(["Time usage " + key, timer.timings[key]])

        return lines

    def get_json(self, timer = None):

        return {
            "summary": self.get_summary(),
            "timings": timer.timings if timer is not None else None,
            "distances": self.distances,
            "timeUsages": self.timeUsages,
            "rmses": self.rmses,
            "fitnesses": self.fitnesses
        }

    def save_plot(self, path):

        self.fig.savefig(path)