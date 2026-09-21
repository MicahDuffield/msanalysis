"""
This example shows how to read in MS spectra, get the relative abundances for
several M/Z of interest, and then plot these abundances.
 
Author: James E. T. Smith <james.smith9113@gmail.com>
Date: 1/16/2020
Updated: 4/15/2020
 
Edited by: Micah H. Duffield 
Ongoing updates (started): 8/17/2026
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from tkinter import filedialog
import tkinter as tk
 
from msanalysis.data_extraction import read_mzXML
from msanalysis.data_processing import get_relative_abundance
from scipy.signal import savgol_filter
 
 
######
# User specified variables
######
# Temperature range for plotting (in degrees Celsius)
x_lim_lower = 40
x_lim_upper = 200
 
# M/Zs of interest
mzs = [85]
 
window_length = 9  # odd integer
polyorder = 1      # polynomial order
 
# Scale value because mzXML gives arb. units — dividing by this is just a visual aid to make the data look cleaner, not a true scaling factor.
scale_value = 1000

#labels for the legend
custom_labels = [
    "0.50 Torr HF",
    "0.25 Torr HF",
    "1.00 Torr HF",
    "0.10 Torr HF",
]

file_colors = [
    "black",
    "tab:blue",
    "tab:green",
    "tab:red",
]

# The order in which you want above to be in 
legend_order = [3,1,0,2]  

labels = [r"$\mathit{{m/z}}$ = {}".format(mz) for mz in mzs]
 
n_pairs = 4  # max number of (mzXML, LabView CSV) pairs to be selected
 
cols = ["time", "block_temp", "powder_bed_temp", "Ar_heater", "probe_chamber",
        "probe_inlet", "probe_exhaust", "etchant mainifold", "block_T",
        "actual_flow", "pid_output"]
 
# Select (mzXML, LabView CSV) pairs one pair at a time, in processing order
root = tk.Tk()
root.withdraw()
 
file_pairs = []  # list of (mzxml_path, labview_path) tuples
 
for i in range(n_pairs):
    mzxml_path = filedialog.askopenfilename(
        title=f"Select mzXML file {i + 1} of {n_pairs} (in plot order)",
        filetypes=[("MassSpec Files", "*.mzXML")]
    )
    if not mzxml_path:
        break  # user hit Cancel -- stop asking for more pairs
 
    labview_path = filedialog.askopenfilename(
        title=f"Select associated LabView CSV file for mzXML file {i + 1}",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not labview_path:
        break  # user hit Cancel mid-pair -- stop here too
 
    file_pairs.append((mzxml_path, labview_path))
 
root.destroy()
 
if not file_pairs:
    raise SystemExit("No file pairs selected.")
 
results = []
 
for mzXML_file, labview_file in file_pairs:
    df = pd.read_csv(labview_file, names=cols, header=0).astype(float)
    df["time"] -= df["time"][0]
    last_lv_time = np.array(df["time"])[-1]
 
    data = read_mzXML(mzXML_file)
    mz, intensities, times = data["mz"], data["intensities"], data["times"]
 
    subset = np.where(times <= last_lv_time)[0]
    times = times[subset]
    intensities = intensities[subset]
 
    results.append({
        "mzXML_file": mzXML_file,
        "labview_file": labview_file,
        "df": df,
        "mz": mz,
        "intensities": intensities,
        "times": times,
    })
 
# Compute per-run abundance data
for res in results:
    df = res["df"]
    times = res["times"]
    mz = res["mz"]
    intensities = res["intensities"]
 
    temp_interp = np.interp(times, df["time"], df["powder_bed_temp"])
    abun = get_relative_abundance(mz, intensities, mzs)
    abun_smooth = [
        savgol_filter(trace, window_length=window_length, polyorder=polyorder)
        for trace in abun
    ]
 
    res["temp_interp"] = temp_interp
    res["abun"] = abun
    res["abun_smooth"] = abun_smooth
 
 
# Plot
#
sns.set_style("whitegrid")
 
fig, axis = plt.subplots(len(mzs), 1, figsize=(11, 11), sharex=True, squeeze=False)
axis = axis.flatten()
 
for f_idx, res in enumerate(results):
    temp_interp = res["temp_interp"]
    abun = res["abun"]
    abun_smooth = res["abun_smooth"]
    file_label = custom_labels[f_idx] if f_idx < len(custom_labels) else os.path.basename(res["mzXML_file"])
    file_color = file_colors[f_idx] if f_idx < len(file_colors) else "black"
 
    for i, (ax, mz_lab) in enumerate(zip(axis, labels)):
        combined_label = f"{file_label} ({mz_lab})" if len(mzs) > 1 else file_label
        ax.plot(temp_interp, abun[i]/scale_value, color=file_color, linewidth=1,
                 alpha=0.25, marker='o', linestyle='None', markersize=2)
        ax.plot(temp_interp, abun_smooth[i]/scale_value, label=combined_label,
                 color=file_color, linewidth=3)
 
for ax in axis:
    ax.set_ylabel("Intesnity (Arb. Units)", fontsize=20, fontweight="bold", fontname="Arial")
 
    handles, leg_labels = ax.get_legend_handles_labels()
    if legend_order is not None:
        handles = [handles[i] for i in legend_order if i < len(handles)]
        leg_labels = [leg_labels[i] for i in legend_order if i < len(leg_labels)]
    leg = ax.legend(handles, leg_labels, fontsize=16, loc="upper left", frameon=False)
 
    for line in leg.get_lines():
        line.set_linewidth(4)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_linewidth(2)
        spine.set_color("black")
    ax.tick_params(axis="both", which="major", direction="out", length=6, width=2, bottom=True, left=True)
    for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
        tick_label.set_fontweight("bold")
        tick_label.set_fontsize(18)
 
axis[-1].set_xlabel("Temperature ($^o$C)", fontsize=20, fontweight="bold", fontname="Arial")
axis[-1].set_xlim(x_lim_lower, x_lim_upper)
fig.align_ylabels(axis)
plt.tight_layout()
plt.show()