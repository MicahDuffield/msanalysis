"""
This example shows how to read a mzXML file and plot the first spectra using matplotlib.

Author: James E. T. Smith <james.smith9113@gmail.com>
Date: 12/12/19

Edited by: Micah H. Duffield 
Ongoing updates (started): 8/17/2026
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse 

from msanalysis.data_extraction import read_mzXML
from msanalysis.sample_data import get_mzXML_sample_path
from gui_file_select import file_selector
from matplotlib.ticker import FixedLocator, MultipleLocator

def average_around_scan(intensities, scan_number, window=50):
    """
    Average intensities over [scan_number - window, scan_number + window],
    clipped to valid array bounds.
    """
    n_scans = intensities.shape[0]
    lower = max(scan_number - window, 0)
    upper = min(scan_number + window + 1, n_scans)  # +1 so it's inclusive
    return np.mean(intensities[lower:upper], axis=0)
 
 
#
# User specified scan numbers -- edit these directly to change what's plotted
#
intended_scan_number = 100
intended_scan_number_2 = 500
window = 50

mzXML_file = file_selector(("MasSpec Files", "*.mzXML"))

#
# Read in mzXML
#
data = read_mzXML(mzXML_file)
mz, intensities, times = data["mz"], data["intensities"], data["times"]

average_intensity_1 = average_around_scan(intensities, intended_scan_number, window=window)
average_intensity_2 = average_around_scan(intensities, intended_scan_number_2, window=window)

#
# Plot
#
plt.figure(figsize=(8, 8))
sns.set_style("whitegrid")
plt.plot(mz, average_intensity_1, c="grey", label="Ar only" )
plt.plot(mz, average_intensity_2+100, c="red", label="HF dose")
plt.xlim((0,110))
plt.ylim((0,10))
plt.xlabel("M/Z", fontsize=28, fontweight="bold",fontname="Arial")
plt.ylabel("Intensity (mV)", fontsize=28, fontweight="bold",fontname="Arial")
plt.tick_params(axis="both", which="major", direction="out",length=6, width=2, bottom=True, left=True, top=False, right=False, labelsize=16)
plt.gca().xaxis.set_minor_locator(MultipleLocator(2))
plt.tick_params(axis="x", which="minor", length=6, width=2.5, bottom=True, top=False)
plt.grid(False)
for spine in plt.gca().spines.values():
    spine.set_linewidth(3)
    spine.set_color("black")
plt.tight_layout()
plt.legend(fontsize=16, loc="upper left", frameon=False)
plt.show()