import sys
import argparse
import random
from pyrosetta import *
from pyrosetta.rosetta.numeric import random
from pyrosetta.rosetta.protocols import moves

init(extra_options="-ignore_unrecognized_res")

parser = argparse.ArgumentParser()
#add line here to add an argument
parser.add_argument('filename')
args = parser.parse_args()
file = args.filename

mypose = pose_from_pdb(file) 
print(f"Loaded pose with {mypose.total_residue()} residues from: {args.filename}")
sxfn = get_score_function()
score = sxfn.score(mypose)
print('++++++++++++++++++++++++++++++++++')
print(score)
the_observer = moves.AddPyMOLObserver(mypose, keep_history=True, update_interval=0)
the_observer.pymol().apply(mypose)

N_residues = mypose.total_residue()
mc = moves.MonteCarlo(mypose, sxfn, 1.0)

for i in range(2):
    # Perturb phi and psi
    rand_residue = random.uniform()
    rand_residue = int(rand_residue * N_residues +1)
    phi_pert = random.gaussian()
    psi_pert = random.gaussian()
    orig_phi = mypose.phi(rand_residue)
    orig_psi = mypose.psi(rand_residue)
    mypose.set_phi(rand_residue, orig_phi + phi_pert)
    mypose.set_psi(rand_residue, orig_psi + psi_pert)
    mc.boltzmann(mypose)
