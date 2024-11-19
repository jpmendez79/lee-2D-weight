# lee-weight.py
# Created by Jesse Mendez <jmend46@lsu.edu>
# Updated 11/08/2024

import ROOT
import ast
import sys
import time
from itertools import islice
from array import array

def progressBar(count_value, total, spinner_chars="/-\|", suffix=''):
    """
    Displays a progress bar with a spinning element and a moving '>' character.
    
    Args:
    - count_value: Current count value in the loop.
    - total: Total value for the loop.
    - spinner_chars: Characters used for the spinner (rotating effect).
    - suffix: A string to append at the end of the progress bar.
    """
    spinner = spinner_chars[count_value % len(spinner_chars)]
    bar_length = 50  # Adjusted for better terminal fit
    filled_up_length = int(bar_length * count_value / float(total))
    percentage = round(100.0 * count_value / float(total), 1)
    
    # Construct the bar with a moving '>' character
    bar = '=' * filled_up_length
    if filled_up_length < bar_length:
        bar += '>'
    bar = bar.ljust(bar_length, '-')
    
    sys.stdout.write(f'\r[{spinner}] [{bar}] {percentage}% ... {suffix}')
    sys.stdout.flush()

def read_config_file(file_path):
    config = {}
    current_key = None
    accumulating_value = ""

    with open(file_path, 'r') as file:
        for line in file:
            # Strip whitespace and skip comments or empty lines
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Check if the line contains '=' indicating a new key-value pair
            if '=' in line and not accumulating_value:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Check if the value starts a multi-line list
                if value.startswith("[") and not value.endswith("]"):
                    current_key = key  # Start accumulating multi-line value
                    accumulating_value = value
                else:
                    # Single-line or complete list, try to evaluate
                    try:
                        config[key] = ast.literal_eval(value)
                    except (ValueError, SyntaxError):
                        config[key] = value

            # Continue accumulating multi-line value
            elif accumulating_value:
                accumulating_value += " " + line
                # Detect the end of the multi-line list
                if line.endswith("]"):
                    try:
                        config[current_key] = ast.literal_eval(accumulating_value)
                    except (ValueError, SyntaxError):
                        config[current_key] = accumulating_value
                    # Reset accumulation
                    accumulating_value = ""
                    current_key = None

    return config


def find_bin(value, edges):

    for bin in range(len(edges) - 1):
        if edges[bin] <= value < edges[bin + 1]:
            # To keep with ROOT histogram binning convention of starting at 1
            return bin + 1

        
def assign_weight(xbin, ybin):

    # Load weights
    weights = config.get("weights")

    # Handle out of bounds x, y and return default weight
    if xbin is None or ybin is None:
        return config.get("default_weight")
    
    # Assign a default weight within bounds of xbin and ybin range
    assigned_weight = config.get("default_weight")
    # Go through list and see if we have a matcning weight
    # print(xbin, ybin)
    for weight in weights:
        if (xbin, ybin) == weight[:2]:
            assigned_weight = weight[-1]

    return assigned_weight


# Set this to true if you want to see all my print statements I used to debug
debug = False


# Read config file
config = read_config_file("lee_2d.conf")

# Read in root file
# Hardcoded for testing purposes
root_file = ROOT.TFile.Open("test_bnb_intrinsic_nue_overlay_run1.root", "UPDATE")
if not root_file or root_file.IsZombie():
    print("Error: Unable to open the file.")
else:
    print("File opened successfully.")

# Read in the ttree that contains our criteria variables
# This will hold our new variable too
T_PFeval_ttree = root_file['wcpselection/T_PFeval']

# Create new branch
new_weight = array('f', [0])


new_branch = T_PFeval_ttree.Branch("truth_2Dlee_weight", new_weight, "truth_2Dlee_weight/F")

loop = 0
for entry in islice(T_PFeval_ttree, 2000):
# for entry in T_PFeval_ttree:
    if debug is True:
        print("Entry", loop)
        print("truth_showerKE", entry.truth_showerKE)

    # Convert from GeV to MeV
    showerKE_MeV = 1000 * entry.truth_showerKE
    if debug is True:
        print(showerKE_MeV)
    # Calculate Cos theta using four momenta
    four_momenta = ROOT.TLorentzVector(entry.truth_showerMomentum[0], entry.truth_showerMomentum[1], entry.truth_showerMomentum[2], entry.truth_showerMomentum[3])
    cos_theta = four_momenta.CosTheta()
    if debug is True:
        print("Cos Theta:", cos_theta)
    # Bin the x and y values
    xbin = find_bin(showerKE_MeV, config.get("x_bin_edges"))
    ybin = find_bin(cos_theta, config.get("y_bin_edges"))
    if debug is True:
        print(xbin)
        print(ybin)

    # Assign a weight
    new_weight[0] = assign_weight(xbin, ybin)
    if debug is True:
        print(new_weight)

    entry.Fill()
    progressBar(loop, 2000, suffix="Processing")
    loop = loop + 1
    if debug is True:
        print("New Branch truth_2Dlee_weight: ", entry.truth_2Dlee_weight)


root_file.cd("wcpselection")
T_PFeval_ttree.Write("", ROOT.TObject.kOverwrite)
print("\nUpdated T_PFeval_ttree written to file")

root_file.Close()
print("Root file closed")
