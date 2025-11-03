import sys
import argparse
from pyrosetta import *

init(extra_options="-ignore_unrecognized_res")

parser = argparse.ArgumentParser()
#add line here to add an argument
parser.add_argument('filename')
args = parser.parse_args()
file = args.filename

mypose = pose_from_pdb(file) # load pose
print(f"Loaded pose with {mypose.total_residue()} residues from: {args.filename}")