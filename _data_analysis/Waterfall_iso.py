import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import numpy as np
from tkinter import filedialog
import tkinter as tk
 
from msanalysis.data_extraction import read_mzXML
from matplotlib.ticker import MultipleLocator
 
 
def average_around_scan(intensities, scan_number, window=50):
    """Average intensities over [scan_number - window, scan_number + window]."""
    n_scans = intensities.shape[0]
    lower = max(scan_number - window, 0)
    upper = min(scan_number + window + 1, n_scans)
    return np.mean(intensities[lower:upper], axis=0)
 
 
#
# Select multiple mzXML files at once
#
root = tk.Tk()
root.withdraw()  # hide the empty root window
file_paths = filedialog.askopenfilenames(
    title="Select up to 12 mzXML files",
    filetypes=[("MassSpec Files", "*.mzXML")]
)
root.destroy()
 
if not file_paths:
    raise SystemExit("No files selected.")
 
#
# Settings
#
scan_number = 500     # scan (or scan-window center) to average around per file
window = 30          # +/- scans to average
y_offset_step = 50   # vertical spacing between stacked spectra -- tune to your data
 
#
# Plot
#
sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(9, 11))
 
# Use a colormap so each file gets a distinct, ordered color
cmap = cm.get_cmap("viridis", len(file_paths))
 
for i, file_path in enumerate(file_paths):
    data = read_mzXML(file_path)
    mz, intensities = data["mz"], data["intensities"]
 
    spectrum = average_around_scan(intensities, scan_number, window=window)
 
    offset = i * y_offset_step
    label = file_path.split("/")[-1]  # just the filename, not full path
 
    ax.plot(mz, spectrum + offset, color=cmap(i), linewidth=1.5, label=label)
 
ax.set_xlabel("M/Z", fontsize=20, fontweight="bold", fontname="Arial")
ax.set_ylabel("Intensity (offset, abs. units)", fontsize=20, fontweight="bold",
              fontname="Arial")
ax.set_xlim(13, 110)  # adjust to your m/z range of interest
ax.tick_params(axis="both", which="major", direction="out", length=6,
                width=2, bottom=True, left=True, top=False, right=False,
                labelsize=14)
ax.xaxis.set_minor_locator(MultipleLocator(2))
ax.tick_params(axis="x", which="minor", length=4, width=1.5, bottom=True)
ax.grid(False)
 
for spine in ax.spines.values():
    spine.set_linewidth(2)
    spine.set_color("black")
 
# Since y-axis is now just "stacked/offset" rather than a real intensity
# scale, it's common to hide the y-tick numbers in a waterfall plot
ax.set_yticks([])
 
ax.legend(fontsize=9, loc="upper left", frameon=False, bbox_to_anchor=(1.02, 1))
plt.xlim((80, 90))
plt.tight_layout()
plt.show()