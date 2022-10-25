import matplotlib.pyplot as plt
from tabulate import tabulate
import statistics

class Plotter:

    def __init__(self, showPlot = True):

        # Initialize plot
        self.plot_x = []

        self.fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, sharex=True, sharey=False)
        self.axes = [ax1, ax2, ax3, ax4, ax5, ax6]

        # Initialize value arrays
        self.distances = []
        self.timeUsages = []
        self.rmses = []
        self.fitnesses = []
        
        self.position_error_2d = []
        self.position_error_3d = []
        self.position_error_x = []
        self.position_error_y = []
        self.position_error_z = []
        self.position_age = []

    def step(self, updatePlot = True):
        self.plot_x.append(len(self.distances) - 1)

        if updatePlot:
            self.update()

    def update(self):
        
        # Enable interactive mode, which redraws plot on change
        plt.ion()

        # Show the plot without blocking
        plt.show(block=False)

        (ax1, ax2, ax3, ax4, ax5, ax6) = self.axes

        for ax in self.axes:
            ax.clear()

        ax1.set_title("Calculation time", fontsize=8)
        ax1.plot(self.plot_x, self.timeUsages, color="blue")
        
        ax2.set_title("Incremental distance", fontsize=8)
        ax2.plot(self.plot_x, self.distances, color="red")
        
        ax3.set_title("Registration error", fontsize=8)
        ax3.plot(self.plot_x, self.rmses, color="purple", label="rmse")
        ax3.plot(self.plot_x, self.fitnesses, color="green", label="fitness")
        ax3.legend(loc="upper left")
        
        if len(self.position_error_3d) > 0:
            ax4.set_title("Positioning errors, individual axes", fontsize=8)
            ax4.plot(self.plot_x, self.position_error_x, color="blue", label="x")
            ax4.plot(self.plot_x, self.position_error_y, color="red", label="y")
            ax4.plot(self.plot_x, self.position_error_z, color="green", label="z")
            ax4.legend(loc="upper left")
            
            ax5.set_title("Positioning errors, combined axes", fontsize=8)
            ax5.plot(self.plot_x, self.position_error_2d, color="blue", label="2d")
            ax5.plot(self.plot_x, self.position_error_3d, color="red", label="3d")
            ax5.legend(loc="upper left")
            
            ax6.set_title("Actual coordinate age", fontsize=8)
            ax6.plot(self.plot_x, self.position_age, color="purple")
        
        ax1.set_ylabel("Seconds")
        ax2.set_ylabel("Meters")
        ax4.set_ylabel("Meters")
        ax5.set_ylabel("Meters")
        ax6.set_ylabel("Seconds")
        
        ax6.set_xlabel("Frame index")

        for ax in self.axes:
            #
            pass

    def destroy(self):
        plt.close(self.fig)

    def print_summary(self, timer = None):

        print(tabulate(self.get_summary(timer)))

    def get_summary(self, timer = None):

        nonPerfect = [x for x in self.fitnesses if x <= 0.95]

        lines = [
            ["Number of frames:", len(self.plot_x) + 1],
            ["Total movement distance:", sum(self.distances)],
            ["Max distance: ", max(self.distances) if len(self.distances) > 0 else float('nan')],
            ["Avg distance: ", statistics.mean(self.distances) if len(self.distances) > 0 else float('nan')],
            ["Min distance: ", min(self.distances) if len(self.distances) > 0 else float('nan')],
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
            "fitnesses": self.fitnesses,
            "position_error_x": self.position_error_x,
            "position_error_y": self.position_error_y,
            "position_error_z": self.position_error_z,
            "position_error_3d": self.position_error_3d
        }

    def save_plot(self, path):

        self.fig.savefig(path)