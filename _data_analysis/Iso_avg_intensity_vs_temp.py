import re
 
import matplotlib.pyplot as plt
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
 
 
def extract_temperature(file_path):
    """
    Pull a temperature value out of a filename like '...25C.mzXML' or
    '...25_C.mzXML' or '...25 C.mzXML'. Returns a float (in whatever
    units your filenames encode, e.g. degrees C).
    """
    filename = file_path.split("/")[-1]
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*_?\s*C(?=[_.\s-]|$)", filename, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find a temperature in filename: {filename}")
    return float(match.group(1))
 
 
#
# User specified variables
#
# M/Z range to sum over
x_lim_lower = 84.5
x_lim_upper = 85.5
 
scan_number = 60      # first scan (or scan-window center) to average around per file
scan_number_2 = 600   # second scan (or scan-window center) to average around per file
scan_window = 9        # +/- scans to average around each scan number
 
n_files = 11        # amount of files to be selected
 
# Select multiple mzXML files individually
root = tk.Tk()
root.withdraw()
 
file_paths = []
for i in range(n_files):
    path = filedialog.askopenfilename(
        title=f"Select file {i + 1} of {n_files}",
        filetypes=[("MassSpec Files", "*.mzXML")]
    )
    if not path:
        break  # user hit Cancel -- stop asking for more files
    file_paths.append(path)
 
root.destroy()
 
if not file_paths:
    raise SystemExit("No files selected.")
 
# Extract temperature + summed intensity (at both scan numbers) for each file
temperatures = []
summed_intensities = []
summed_intensities_2 = []
labels = []
 
for file_path in file_paths:
    data = read_mzXML(file_path)
    mz, intensities = data["mz"], data["intensities"]
    mz_mask = (mz >= x_lim_lower) & (mz <= x_lim_upper)
 
    # First scan window
    avg_spectrum = average_around_scan(intensities, scan_number, window=scan_window)
    summed_intensity = np.sum(avg_spectrum[mz_mask])
 
    # Second scan window
    avg_spectrum_2 = average_around_scan(intensities, scan_number_2, window=scan_window)
    summed_intensity_2 = np.sum(avg_spectrum_2[mz_mask])
 
    temperature = extract_temperature(file_path)
 
    temperatures.append(temperature)
    summed_intensities.append(summed_intensity)
    summed_intensities_2.append(summed_intensity_2)
    labels.append(file_path.split("/")[-1])

# Sort everything by temperature (same order works for both series since
# they share the same file list / temperature list)
temperatures = np.array(temperatures)
summed_intensities = np.array(summed_intensities)
summed_intensities_2 = np.array(summed_intensities_2)
 
order = np.argsort(temperatures)
temperatures_sorted = temperatures[order]
summed_intensities = summed_intensities[order]
summed_intensities_2 = summed_intensities_2[order]
 

# Plot
#
sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(9, 7))
 
ax.plot(temperatures_sorted, summed_intensities, marker="o", color="tab:red",
        linewidth=1.5, markersize=8, label=f"Ar only")
ax.plot(temperatures_sorted, summed_intensities_2, marker="o", color="tab:blue",
        linewidth=1.5, markersize=8, label=f"HF dose")
 
ax.set_xlabel("Temperature (\u00b0C)", fontsize=20, fontweight="bold", fontname="Arial")
ax.set_ylabel(r"$\mathbf{m/z}=$" + "85 integrated intensity (counts)",
              fontsize=20, fontweight="bold", fontname="Arial")
 
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.tick_params(axis="both", which="major", direction="out", length=6,
                width=2, bottom=True, left=True, top=False, right=False,
                labelsize=14)
ax.grid(False)
ax.legend(fontsize=12, frameon=False)
 
for spine in ax.spines.values():
    spine.set_linewidth(2)
    spine.set_color("black")
 
plt.tight_layout()
plt.show()