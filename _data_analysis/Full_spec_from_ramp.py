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
 
 
# User specified variables -- edit these directly to change what's plotted

#scan numbers to average around for plotting
intended_scan_number = 100
intended_scan_number_2 = 500
window = 50

temp_value_lower = 25
temp_value_upper = 160

#temperature limits for plotting
x_lim_lower = 0
x_lim_upper = 110

#intensity limits for plotting
y_lim_lower = 0
y_lim_upper = 10

#offset for plotting the second spectrum
offset = 0

#first select the mzXML path
mzXML_file = file_selector(("MasSpec Files", "*.mzXML"))
labview_file = file_selector(("CSV Files", "*.csv"))

#
# Read CSV Data from LabView
#
cols = ["time", "block_temp", "powder_bed_temp", "Ar_heater", "probe_chamber", "probe_inlet", "probe_exhaust", "etchant mainifold", "block_T", "actual_flow", "pid_output"]
#, "cold_cathode", "hot_cathode"

# this reads the csv selected and does a few things
# The column names from the csv file are removed by using header=0
# The columns are given names compatible with pandas with names=cols
# The values are read in as floats, not strings. 
df = pd.read_csv(labview_file, names=cols, header=0).astype(float)
# #convert all strings to numbers!
df["time"] -= df["time"][0]
last_lv_time = np.array(df["time"])[-1]

#
# Read in mzXML
#
data = read_mzXML(mzXML_file)
mz, intensities, times = data["mz"], data["intensities"], data["times"]
# Only go as far as LabView data (which we are assuming is always shut off after the mass spec)
subset = np.where(times <= last_lv_time)[0]
times = times[subset]
intensities = intensities[subset]

#
# Use timestamps from mzXML and Labview to interpolate temperature for each scan
#
temp_interp = np.interp(times, df["time"], df["powder_bed_temp"])

scan_number_lower = np.where((temp_interp >= temp_value_lower))[0][0]
scan_number_upper = np.where((temp_interp <= temp_value_upper))[0][-1]

average_intensity_1 = average_around_scan(intensities, scan_number_lower, window=window)
average_intensity_2 = average_around_scan(intensities, scan_number_upper, window=window)

#
# Plot
#
plt.figure(figsize=(8, 8))
sns.set_style("whitegrid")
plt.plot(mz, average_intensity_1, c="grey", label=f"{temp_value_lower} $^o$C") 
plt.plot(mz, average_intensity_2+offset, c="red", label=f"{temp_value_upper} $^o$C")
plt.xlim((x_lim_lower,x_lim_upper))
plt.ylim((y_lim_lower,y_lim_upper))
plt.xlabel("m/z", fontsize=28, fontweight="bold",fontname="Arial")
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

