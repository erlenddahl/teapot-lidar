import matplotlib.pyplot as plt
from tabulate import tabulate
import statistics

class Plotter:

    def __init__(self, show_plot = True):

        # Initialize plot
        self.plot_x = []

        self.fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7) = plt.subplots(7, sharex=True, sharey=False)
        self.axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7]

        # Initialize value arrays
        self.distances = []
        self.timeUsages = []
        self.rmses = []
        self.fitnesses = []
        
        self.position_error_2d = []
        self.position_error_3d = []
        self.position_error_along_heading = []
        self.position_error_across_heading = []
        self.position_error_y = []
        self.position_error_x = []
        self.position_error_y = []
        self.position_error_z = []
        self.position_age = []

        self.is_showing = False
        
        if show_plot:
            self.show_plot()

    def show_plot(self):
        # Enable interactive mode, which redraws plot on change
        plt.ion()

        # Show the plot without blocking
        plt.show(block=False)

        self.is_showing = True

    def step(self, update_plot = True):
        self.plot_x.append(len(self.distances) - 1)

        if update_plot:
            self.update()

    def update(self):

        (ax1, ax2, ax3, ax4, ax5, ax6, ax7) = self.axes

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
            
            ax7.set_title("Positioning errors along/across heading, combined axes", fontsize=8)
            ax7.plot(self.plot_x, self.position_error_along_heading, color="blue", label="along")
            ax7.plot(self.plot_x, self.position_error_across_heading, color="red", label="across")
            ax7.plot(self.plot_x, self.position_error_z, color="green", label="z")
            ax7.legend(loc="upper left")
        
        ax1.set_ylabel("Seconds")
        ax2.set_ylabel("Meters")
        ax4.set_ylabel("Meters")
        ax5.set_ylabel("Meters")
        ax6.set_ylabel("Seconds")
        ax7.set_ylabel("Meters")
        
        ax7.set_xlabel("Frame index")

        self.fig.canvas.draw()

    def destroy(self):
        plt.close(self.fig)

    def print_summary(self, timer = None):

        print(tabulate(self.get_summary(timer)))

    def get_summary(self, timer = None):

        nonPerfect = [x for x in self.fitnesses if x <= 0.95]

        has_pos_error = len(self.position_error_x) > 0

        lines = [
            ["Number of frames:", len(self.plot_x) + 1],
            ["Total movement distance:", sum(self.distances)],
            ["Max distance: ", max(self.distances) if len(self.distances) > 0 else float('nan')],
            ["Avg distance: ", statistics.mean(self.distances) if len(self.distances) > 0 else float('nan')],
            ["Min distance: ", min(self.distances) if len(self.distances) > 0 else float('nan')],
            ["Max time: ", max(self.timeUsages) if len(self.timeUsages) > 0 else float('nan')],
            ["Avg time: ", statistics.mean(self.timeUsages) if len(self.timeUsages) > 0 else float('nan')],
            ["Min time: ", min(self.timeUsages) if len(self.timeUsages) > 0 else float('nan')],
            ["Max fitness: ", max(self.fitnesses) if len(self.fitnesses) > 0 else float('nan')],
            ["Avg fitness: ", statistics.mean(self.fitnesses) if len(self.fitnesses) > 0 else float('nan')],
            ["Avg non-perfect fitness: ", statistics.mean(nonPerfect) if len(nonPerfect) > 0 else "-"],
            ["Min fitness: ", min(self.fitnesses) if len(self.fitnesses) > 0 else float('nan')],
            ["Max rmse: ", max(self.rmses) if len(self.rmses) > 0 else float('nan')],
            ["Avg rmse: ", statistics.mean(self.rmses) if len(self.rmses) > 0 else float('nan')],
            ["Min rmse: ", min(self.rmses) if len(self.rmses) > 0 else float('nan')],
            
            ["Avg error x: ", statistics.mean(self.position_error_x) if has_pos_error else float('nan')],
            ["Avg error y: ", statistics.mean(self.position_error_y) if has_pos_error else float('nan')],
            ["Avg error z: ", statistics.mean(self.position_error_z) if has_pos_error else float('nan')],
            ["Avg error 2d: ", statistics.mean(self.position_error_2d) if has_pos_error else float('nan')],
            ["Avg error 3d: ", statistics.mean(self.position_error_3d) if has_pos_error else float('nan')],
            
            ["Final error 2d: ", self.position_error_2d[-1] if has_pos_error else float('nan')],
            ["Final error 3d: ", self.position_error_3d[-1] if has_pos_error else float('nan')],
            
            ["Final error along heading: ", self.position_error_along_heading[-1] if has_pos_error else float('nan')],
            ["Final error across heading: ", self.position_error_across_heading[-1] if has_pos_error else float('nan')]
        ]

        if timer is not None:
            for key in timer.timings:
                lines.append(["Time usage " + key, timer.timings[key]])

        return lines

    def get_json(self, timer = None):

        return {
            "summary": self.get_summary(),
            "timings": timer.timings if timer is not None else None,
        }

    def save_plot(self, path):
        self.fig.canvas.draw()
        self.fig.savefig(path)