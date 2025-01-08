# lee-weight.py
# Created by Jesse Mendez <jmend46@lsu.edu>
# Updated 11/27/2024

import ROOT
import ast
import sys
import argparse
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
    # Ensure that the filled length doesn't exceed the bar length
    filled_up_length = int(bar_length * count_value / float(total))
    percentage = round(100.0 * count_value / float(total), 1)
    
    # Construct the bar with a moving '>' character
    bar = '=' * filled_up_length
    if filled_up_length < bar_length:
        bar += '>'
    bar = bar.ljust(bar_length, '-')
    
    # Ensure the percentage never exceeds 100%
    if count_value >= total:
        percentage = 100
        bar = '=' * bar_length  # Make sure the bar is full when 100%
    
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

# Initialize the parser
parser = argparse.ArgumentParser(description="A script to add weights to T_PFeval TTree.")

parser.add_argument("-q", "--quiet", action="store_true", help="Suppress all script terminal output.")
parser.add_argument("-c", "--config", type=str, help="Specify a configuration file.")
parser.add_argument("-v", "--verbose", action="store_true", help="Turn on all debugging messages. This overrides the -q option.")
# Add the positional argument for the filename
parser.add_argument("filename", nargs="?", help="The root file you want to reweight.")

# Parse the arguments
args = parser.parse_args()

# Check if the filename is missing
if args.filename is None:
    print("Error: You must provide a root file as the last argument.")
    parser.print_help()  # Print the help message
    sys.exit(1)
if args.config is None:
    print("Error: You must provide a config file path using -c.")
    sys.exit(1)

# Access the arguments
if args.config:
    print(f"Using configuration file: {args.config}")
print(f"Processing file: {args.filename}")


# Set this to true if you want to see all my print statements I used to debug
# debug = False


# Read config file
config = read_config_file(args.config)

# Read in root file
root_file = ROOT.TFile.Open(args.filename, "UPDATE")
if not root_file or root_file.IsZombie():
    print("Error: Unable to open the file.")
else:
    print("File opened successfully.")

# Read in the ttree that contains our criteria variables
# Read in ttree that will be the final place for our new variable
T_PFeval_ttree = root_file['wcpselection/T_PFeval']
tree_eval = root_file.Get("wcpselection/T_eval")
# Create new branch
new_weight = array('f', [0])


new_branch = tree_eval.Branch("weight_2Dlee", new_weight, "weight_2Dlee/F")
total_events = tree_eval.GetEntries()
update_interval = 100
print(total_events)
for i, entry in enumerate(islice(tree_eval, total_events)):    
# for entry in tree_eval:        
    progressBar(i, total_events, suffix="Processing")

    # Load variables for calculation
    T_PFeval_ttree.GetEntry(i)
    truth_showerKE = getattr(T_PFeval_ttree, "truth_showerKE")
    truth_showerMomentum = getattr(T_PFeval_ttree, "truth_showerMomentum")
    if args.verbose is True:
        print("Entry", i)
        print("truth_showerKE", truth_showerKE)

    # Convert from GeV to MeV
    showerKE_MeV = 1000 * truth_showerKE
    if args.verbose is True:
        print(showerKE_MeV)
    # Calculate Cos theta using four momenta
    four_momenta = ROOT.TLorentzVector(truth_showerMomentum[0], truth_showerMomentum[1], truth_showerMomentum[2], truth_showerMomentum[3])
    cos_theta = four_momenta.CosTheta()
    if args.verbose is True:
        print("Cos Theta:", cos_theta)
    # Bin the x and y values
    xbin = find_bin(showerKE_MeV, config.get("x_bin_edges"))
    ybin = find_bin(cos_theta, config.get("y_bin_edges"))
    if args.verbose is True:
        print(xbin)
        print(ybin)

    # Load the T-eval entry to copy over new variable
    # Assign a weight
    new_weight[0] = assign_weight(xbin, ybin)
    if args.verbose is True:
        print(new_weight)
        
    new_branch.Fill()
    i = i+1
    if args.verbose is True:
        print("New Branch truth_2Dlee_weight: ", entry.truth_2Dlee_weight)


root_file.cd("wcpselection")
tree_eval.Write("", ROOT.TObject.kOverwrite)
print("\nUpdated T_eval_ttree written to file")

root_file.Close()
print("Root file closed")
