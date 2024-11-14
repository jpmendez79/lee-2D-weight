import ROOT
import numpy as np
import ctypes
from itertools import islice

# Load the ROOT file and access the TTree
file_name = "test_bnb_intrinsic_nue_overlay_run1.root"
tree_name = "wcpselection/T_PFeval"
root_file = ROOT.TFile.Open(file_name)
tree = root_file.Get(tree_name)

# # Define custom bin edges for each axis
# x_bin_edges = np.array([140, 300, 450, 620, 800, 1200], dtype=np.float64)
# y_bin_edges = np.array([-1, -0.6667, -0.3333, 0, 0.3, 0.72, 1])
# x_bins = len(x_bin_edges) - 1
# y_bins = len(y_bin_edges) - 1

# # Create the 2D histogram with the custom bin edges
# hist = ROOT.TH2D("hist", "2D Histogram;X variable;Y variable", x_bins, x_bin_edges, y_bins, y_bin_edges)

# # Loop over the events in the TTree and fill the histogram
# for entry in tree:
#     x_value = getattr(entry, "truth_showerKE")  # Replace 'x_var' with the name of your X variable in the TTree
#     y_value = getattr(entry, "truth_2Dlee_weight")  # Replace 'y_var' with the name of your Y variable in the TTree
#     hist.Fill(x_value, y_value)

# # Draw the histogram
# canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
# hist.Draw("COLZ")
# canvas.SaveAs("2D_histogram.png")  # Save the plot as a PNG image

# # Close the ROOT file
# root_file.Close()

# Plot Truth Electron Energy
h1 = ROOT.TH1D("h1", "Hist", 30, 0, 4)
h2 = ROOT.TH1D("h2", "Hist", 30, 0, 4)
for entry in islice(tree, 2000):
# for entry in tree:
    x_value = getattr(entry, "truth_showerKE")
    four_momenta = ROOT.TLorentzVector(entry.truth_showerMomentum[0], entry.truth_showerMomentum[1], entry.truth_showerMomentum[2], entry.truth_showerMomentum[3])
    cos_theta = four_momenta.CosTheta()
#     y_value = getattr(entry, "truth_2Dlee_weight")
    lee_2d_weight = getattr(entry, "truth_2Dlee_weight")
    print("Start")
    print(x_value)
    print(cos_theta)
    print(lee_2d_weight)
    print("End")
    h1.Fill(x_value)
    h2.Fill(x_value, lee_2d_weight)

h1.SetLineColor(ROOT.kRed)
h1.SetLineWidth(2)
h2.SetLineColor(ROOT.kBlue)
h2.SetLineWidth(2)
# Draw the histogram
canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
h1.Draw()
h2.Draw("SAME")
canvas.SaveAs("truth_ke20bin_30bin.png")  # Save the plot as a PNG image
