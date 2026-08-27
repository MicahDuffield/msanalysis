"""
This example shows how to read in MS spectra, get the relative abundances for
several M/Z of interest, and then plot these abundances.

Author: James E. T. Smith <james.smith9113@gmail.com>
Date: 1/16/2020
Updated: 4/15/2020

Edited by: Micah H. Duffield 
Ongoing updates (started): 8/17/2026
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from msanalysis.data_extraction import read_mzXML
from msanalysis.data_processing import get_relative_abundance
from msanalysis.sample_data import get_mzXML_sample_path, get_csv_sample_path
from gui_file_select import file_selector
from matplotlib.ticker import FixedLocator
from scipy.signal import savgol_filter

#
# User specified variables
#

# Users can specify their own path like the lines below
# labview_file = "/home/james/Downloads/20200228_TP.csv"
# mzXML_file = "/home/james/Downloads/20200228_1175.mzXML"
# labview_file = "20200612_TP.csv"
# mzXML_file = "20200612_2735.mzXML"

#first select the mzXML path
mzXML_file = file_selector(("MasSpec Files", "*.mzXML"))

#
# Read in mzXML
#
data = read_mzXML(mzXML_file)
mz, intensities, times = data["mz"], data["intensities"], data["times"]
times = times / 60

#
# Get abundances
#
mzs = [20,85,17]
abun = get_relative_abundance(mz, intensities, mzs)

window_length = 9  # odd integer
polyorder = 1       # polynomial order
 
abun_smooth = [
    savgol_filter(trace, window_length=window_length, polyorder=polyorder)
    for trace in abun
]

#
# Plot
#
sns.set_style("whitegrid")

mz_colors = {20: "tab:blue", 17: "purple", 85: "tab:red", 104: "tab:green"}
colors = [mz_colors[mz] for mz in mzs]
labels = [r"$\mathit{{M/z}}$ = {}".format(mz) for mz in mzs]

fig, axis = plt.subplots(len(mzs), 1, figsize=(11, 11), sharex=True)

for i, (ax, lab, color) in enumerate(zip(axis, labels, colors)):
    ax.plot(times, abun[i], color=color, linewidth=1, alpha=0.25, marker='o',linestyle='None', markersize=2)
    ax.plot(times, abun_smooth[i], label=lab, color=color, linewidth=3)
    ax.set_ylabel("Intensity (abs. units)", fontsize=20, fontweight="bold",fontname="Arial")
    leg = ax.legend(fontsize=16, loc="upper left", frameon=False)
    for line in leg.get_lines():
        line.set_linewidth(4)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_linewidth(2)
        spine.set_color("black")
    ax.tick_params(axis="both", which="major", direction="out",length=6, width=2, bottom=True, left=True)
    for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
        tick_label.set_fontweight("bold")
        tick_label.set_fontsize(18)
axis[-1].set_xlabel("Time (mins)", fontsize=20, fontweight="bold",fontname="Arial")
axis[-1].set_xlim(0, 75)
fig.align_ylabels(axis)
plt.tight_layout()
plt.show()

