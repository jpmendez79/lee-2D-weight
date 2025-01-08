import ROOT
import ctypes
from itertools import islice
import array
# Load the ROOT file and access the TTree
file_name = "nue_run3.root"
tree_name = "wcpselection/T_PFeval"
root_file = ROOT.TFile.Open(file_name)
tree_pfeval = root_file.Get("wcpselection/T_PFeval")
tree_eval = root_file.Get("wcpselection/T_eval")

# Global 2D Bin Edges
x_bin_edges = [140, 300, 450, 620, 800, 1200]
n_xbins = len(x_bin_edges) - 1  # Number of bins is one less than the number of edges
# Convert bin edges to a C-style array
bin_xedges_array = array.array('d', x_bin_edges)

# True Electron Cos theta
y_bin_edges = [-1, -0.6667, -0.3333, 0, 0.3, 0.72, 1]
n_ybins = len(y_bin_edges) - 1  # Number of bins is one less than the number of edges

# Convert bin edges to a C-style array
bin_yedges_array = array.array('d', y_bin_edges)

# For each plot I want to make
# Get intrinsic nue histogram
# Create weight_lee hist by stacking an applied weight hist on top of nue
# Repeat for weight_2Dlee

# Shower KE
if(0):
    # Plot Truth Electron Energy
    inue_hist = ROOT.TH1D("h1", "Intrinsic Nue", 30, 0, 4.5)
    lee_delta = ROOT.TH1D("h2", "LEE Weight", 30, 0, 4.5)
    lee2d_delta = ROOT.TH1D("h3", "2D LEE Weight", 30, 0, 4.5)
    total_events = tree_eval.GetEntries()
    for i, entry in enumerate(islice(tree_pfeval, total_events)):
        # for entry in tree:
        electron_KE = entry.truth_showerKE
        tree_eval.GetEntry(i)
        lee = getattr(tree_eval, "weight_lee")
        lee_2d_weight = getattr(tree_eval, "weight_2Dlee")
        
        inue_hist.Fill(electron_KE)
        lee_delta.Fill(electron_KE, lee)
        lee2d_delta.Fill(electron_KE, lee_2d_weight)


    inue_hist.SetLineColor(ROOT.kBlue)
    lee_delta.SetLineColor(ROOT.kGreen)
    lee2d_delta.SetLineColor(ROOT.kRed)

    # Create Proper stacks
    # Add 
    lee_stack = ROOT.THStack("hs1", "Comparisons of LEE and 2D LEE;Electron KE [MeV];Entries")

    lee_stack.Add(inue_hist)
    lee_stack.Add(lee_delta)
    lee_stack.SetMaximum(30000)

    lee2d_stack = ROOT.THStack("hs2", "2D LEE Weight")
    lee2d_stack.Add(inue_hist)
    lee2d_stack.Add(lee2d_delta)

    
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    # legend = ROOT.TLegend(0.1, 0.4, 0.3, 0.6)
    legend.AddEntry(inue_hist)
    legend.AddEntry(lee_delta)
    legend.AddEntry(lee2d_delta)
    # Draw the histogram
    canvas = ROOT.TCanvas("canvas", "Canvas")
    canvas.SetLeftMargin(0.15)  # Increase left margin to accommodate the y-axis
    # canvas.SetRightMargin(0.05)  # Adjust the right margin as needed
    lee_stack.Draw("HIST")
    lee2d_stack.Draw("HIST SAME")
    inue_hist.Draw("HIST SAME")
    legend.Draw()
    canvas.RedrawAxis()
    canvas.SaveAs("electron_KE_30bin.png")  # Save the plot as a PNG image

# Cos Theta
if (0):
    # Plot Truth Electron Energy
    inue_hist = ROOT.TH1D("h1", "Intrinsic Nue", 30, -1, 1)
    lee_delta = ROOT.TH1D("h2", "LEE Weight", 30, -1, 1)
    lee2d_delta = ROOT.TH1D("h3", "2D LEE Weight", 30, -1, 1)
    total_events = tree_eval.GetEntries()
    for i, entry in enumerate(islice(tree_pfeval, total_events)):
        # for entry in tree:
        four_momenta = ROOT.TLorentzVector(entry.truth_showerMomentum[0], entry.truth_showerMomentum[1], entry.truth_showerMomentum[2], entry.truth_showerMomentum[3])
        cos_theta = four_momenta.CosTheta()
        tree_eval.GetEntry(i)
        lee = getattr(tree_eval, "weight_lee")
        lee_2d_weight = getattr(tree_eval, "weight_2Dlee")
        
        inue_hist.Fill(cos_theta)
        lee_delta.Fill(cos_theta, lee)
        lee2d_delta.Fill(cos_theta, lee_2d_weight)


    inue_hist.SetLineColor(ROOT.kBlue)
    lee_delta.SetLineColor(ROOT.kGreen)
    lee2d_delta.SetLineColor(ROOT.kRed)

    # Create Proper stacks
    # Add 
    lee_stack = ROOT.THStack("hs1", "Comparisons of LEE and 2D LEE;Electron Cos #theta ;Entries")

    lee_stack.Add(inue_hist)
    lee_stack.Add(lee_delta)
    lee_stack.SetMaximum(40000)

    lee2d_stack = ROOT.THStack("hs2", "2D LEE Weight")
    lee2d_stack.Add(inue_hist)
    lee2d_stack.Add(lee2d_delta)

    

    legend = ROOT.TLegend(0.3, 0.3, 0.5, 0.5)
    legend.AddEntry(inue_hist)
    legend.AddEntry(lee_delta)
    legend.AddEntry(lee2d_delta)
    # Draw the histogram
    canvas = ROOT.TCanvas("canvas", "Canvas")
    canvas.SetLeftMargin(0.15)  # Increase left margin to accommodate the y-axis
    # canvas.SetRightMargin(0.05)  # Adjust the right margin as needed
    lee_stack.Draw("HIST")
    lee2d_stack.Draw("HIST SAME")
    inue_hist.Draw("HIST SAME")
    legend.Draw()
    canvas.RedrawAxis()
    canvas.SaveAs("cos_theta_30bin.png")  # Save the plot as a PNG image




# 2D Distribution of Events
if (1):
    inue_hist = ROOT.TH2D("h1", "Intrinsic Nue;Truth ShowerKE (MeV);Truth Cos#theta;", n_xbins, bin_xedges_array, n_ybins, bin_yedges_array)
    lee_delta = ROOT.TH2D("h2", "LEE Weight;Truth ShowerKE (MeV);Truth Cos#theta;", n_xbins, bin_xedges_array, n_ybins, bin_yedges_array)
    lee2d_delta = ROOT.TH2D("h3", "2D LEE Weight;Truth ShowerKE (MeV);Truth Cos#theta;", n_xbins, bin_xedges_array, n_ybins, bin_yedges_array)
    total_events = tree_eval.GetEntries()
    for i, entry in enumerate(islice(tree_pfeval, total_events)):
        # for entry in tree:
        electron_KE = entry.truth_showerKE*1000
        four_momenta = ROOT.TLorentzVector(entry.truth_showerMomentum[0], entry.truth_showerMomentum[1], entry.truth_showerMomentum[2], entry.truth_showerMomentum[3])
        cos_theta = four_momenta.CosTheta()
        tree_eval.GetEntry(i)
        lee = getattr(tree_eval, "weight_lee")
        lee_2d_weight = getattr(tree_eval, "weight_2Dlee")

        inue_hist.Fill(electron_KE, cos_theta)
        lee_delta.Fill(electron_KE, cos_theta, lee)
        lee2d_delta.Fill(electron_KE, cos_theta, lee_2d_weight)


    canvas = ROOT.TCanvas("canvas", "Canvas", 860,600)
    canvas.SetRightMargin(-0.15)  # Adjust the right margin as needed
    canvas.SetBottomMargin(-0.05)
    inue_hist.SetStats(0)
    lee_delta.SetStats(0)
    lee2d_delta.SetStats(0)

    lee_stack = ROOT.THStack("hs1", "Comparisons of LEE and 2D LEE;Electron Cos #theta ;Entries")

    lee_stack.Add(inue_hist)
    lee_stack.Add(lee_delta)


    lee2d_stack = ROOT.THStack("hs2", "2D LEE Weight")
    lee2d_stack.Add(inue_hist)
    lee2d_stack.Add(lee2d_delta)

    # Pull out the histograms from the stack
    lee_hist = lee_stack.GetStack().Last().Clone("h_lee")
    lee2d_hist = lee2d_stack.GetStack().Last().Clone("h_lee2d")

    if (0): # Normalize the histograms
        lee_hist.Scale(1/total_events)
        lee2d_hist.Scale(1/total_events)

    lee_hist.SetMaximum(0.2)
    lee2d_hist.SetMaximum(0.2)

    # Intrinisc dist only
    if(0):
          inue_hist.Draw("COLZ")
          canvas.SaveAs("intrinsic_KE_vs_cos_theta.png")  # Save the plot as a PNG image
    # Lee Delta dist only
    if(0):
          lee_delta.Draw("COLZ")
          canvas.SaveAs("lee_delta_KE_vs_cos_theta.png")  # Save the plot as a PNG image
    # Lee Delta dist only
    if(0):
          lee2d_delta.Draw("COLZ")
          canvas.SaveAs("lee2d_delta_KE_vs_cos_theta.png")  # Save the plot as a PNG image

    if (0):
        lee_hist.SetTitle("LEE Model")
        lee_hist.Draw("COLZ")
        canvas.SaveAs("lee_KE_vs_cos_theta.png")

    if (0):
        lee2d_hist.SetTitle("2D LEE Model")
        lee2d_hist.Draw("COLZ")
        canvas.SaveAs("lee2d_KE_vs_cos_theta.png")

    # Delta 2D Intrinsic Nue          
    if(0):
        # Pull out the combined histogram from the stack
        
        
        # Clone histB to create a histogram for the ratio
        # Hist A = lee2d Hist B = inue_hist
        rel_diff= lee2d_hist.Clone("ratio")
        rel_diff.Reset()
        rel_diff.SetTitle("Relative Difference 2D LEE and Intrinsic#nu_{e} ")
        for x in range(1, lee2d_hist.GetNbinsX() + 1):
            for y in range(1, lee2d_hist.GetNbinsY() + 1):
                inue_count = inue_hist.GetBinContent(x, y)
                lee2d_count = lee2d_hist.GetBinContent(x, y)
                if (inue_count != 0):
                    diff = -(lee2d_count - inue_count) / inue_count
                    rel_diff.SetBinContent(x, y, diff)
                else: rel_diff.SetBinContent(x, y, 0)
        # rel_diff.Scale(1/total_events)
        rel_diff.SetMaximum(1.4)
        canvas.SetRightMargin(-0.1)  # Adjust the right margin as needed
        rel_diff.Draw("COLZ")
        canvas.SaveAs("diff_lee2d_inue.png")  # Save the plot as a PNG image

        
    # Delta 2D Models          
    if(0):
        # Pull out the combined histogram from the stack
        
        
        # Clone histB to create a histogram for the ratio
        # Hist A = lee2d Hist B = lee
        rel_diff= lee2d_hist.Clone("ratio")
        rel_diff.Reset()
        rel_diff.SetTitle("Relative Difference lee and lee 2d models ")
        for x in range(1, lee_hist.GetNbinsX() + 1):
            for y in range(1, lee_hist.GetNbinsY() + 1):
                lee_count = lee_hist.GetBinContent(x, y)
                lee2d_count = lee2d_hist.GetBinContent(x, y)
                if (lee_count != 0):
                    diff = (lee2d_count - lee_count) / lee_count
                    rel_diff.SetBinContent(x, y, diff)
                else: rel_diff.SetBinContent(x, y, 0)
        rel_diff.Scale(1/total_events)
        rel_diff.SetMaximum(0.00012)
        canvas.SetRightMargin(-0.1)  # Adjust the right margin as needed
        rel_diff.Draw("COLZ")
        canvas.SaveAs("diff_lee2d_lee.png")  # Save the plot as a PNG image

    # Validation Plot         
    if (1):
        # Pull out the combined histogram from the stack
                
        # Clone histB to create a histogram for the ratio
        # Hist A = lee2d Hist B = lee
        val_hist= lee2d_hist.Clone("validation")
        val_hist.Reset()
        val_hist.SetTitle("Validation recovery of weights used Run3")
        for x in range(1, inue_hist.GetNbinsX() + 1):
            for y in range(1, inue_hist.GetNbinsY() + 1):
                lee2d_count = lee2d_hist.GetBinContent(x, y)
                inue_count = inue_hist.GetBinContent(x, y)
                if (inue_count != 0):
                    recovered_weight = (lee2d_count / inue_count) - 1
                    val_hist.SetBinContent(x, y, recovered_weight)
                else: val_hist.SetBinContent(x, y, 0)
        
        # canvas.SetRightMargin(-0.1)  # Adjust the right margin as needed
        val_hist.SetMaximum(11)
        val_hist.SetMarkerColor(ROOT.kWhite)
        ROOT.gStyle.SetPalette(55)
        val_hist.SetContour(20)  # 20 color levels in the Z-axis gradient
        val_hist.Draw("COLZ TEXT")
        canvas.SaveAs("r3_validation_plot.png")  # Save the plot as a PNG image

