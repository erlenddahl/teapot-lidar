import matplotlib.pyplot as plt

class Plotter:

    def __init__(self):
        # Enable interactive mode, which redraws plot on change
        plt.ion()

        # Initialize plot
        self.plot_x = []

        # Show the plot without blocking
        plt.show(block=False)
        self.fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False)
        self.axes = [ax1, ax2, ax3]

        # Initialize value arrays
        self.distances = []
        self.timeUsages = []
        self.rmses = []
        self.fitnesses = []

    def update(self):
        self.plot_x.append(len(self.distances) - 1)

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