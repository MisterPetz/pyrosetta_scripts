import sys
import argparse
import random
from pyrosetta import *
from pyrosetta.rosetta.numeric import random
from pyrosetta.rosetta.protocols import moves
from pyrosetta.rosetta import core
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

the_observer = moves.AddPyMOLObserver(mypose)
the_observer.pymol().apply(mypose)

N_residues = mypose.total_residue()
mc = moves.MonteCarlo(mypose, sxfn, 1.0)

# Set up MoveMap for backbone and sidechain movement
movemap = core.kinematics.MoveMap()
movemap.set_bb(True)
movemap.set_chi(True)
# Minimizer setup
min_opts = core.optimization.MinimizerOptions("lbfgs_armijo_atol", 0.01, True)
minimizer = core.optimization.AtomTreeMinimizer()

for i in range(1):
    # Perturb phi and psi
    rand_residue = random.uniform()
    rand_residue = int(rand_residue * N_residues +1)
    phi_pert = random.gaussian()
    psi_pert = random.gaussian()
    orig_phi = mypose.phi(rand_residue)
    orig_psi = mypose.psi(rand_residue)
    mypose.set_phi(rand_residue, orig_phi + phi_pert)
    mypose.set_psi(rand_residue, orig_psi + psi_pert)
    #add packing and minimization calls to 
    tf = core.pack.task.TaskFactory()
    task = tf.create_task_and_apply_taskoperations(mypose)
    task.restrict_to_repacking()
    core.pack.pack_rotamers(mypose, sxfn, task)
    

    minimizer.run(mypose, movemap, sxfn, min_opts)
    mc.boltzmann(mypose)
    
print(f"Score: {sxfn.score(mypose)}")
print(f"Score of lowest scoirng pose: {sxfn.score(mc.lowest_score_pose())}")
mypose.dump_pdb("Output.pdb")