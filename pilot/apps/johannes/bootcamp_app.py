import sys
import argparse
import random
from pyrosetta import *
from pyrosetta.rosetta.numeric import random
from pyrosetta.rosetta.protocols import moves
from pyrosetta.rosetta import core
from bootcamp_protocol import fold_tree_from_ss


def mc_loop(pose, sxfn):

    N_residues = pose.total_residue()
    mc = moves.MonteCarlo(pose, sxfn, 1.0)

    # Set up MoveMap for backbone and sidechain movement
    movemap = core.kinematics.MoveMap()
    movemap.set_bb(True)
    movemap.set_chi(True)
    # Minimizer setup
    min_opts = core.optimization.MinimizerOptions("lbfgs_armijo_atol", 0.01, True)
    minimizer = core.optimization.AtomTreeMinimizer()

    accepted = 0
    itterations = 35
    sum_score = 0

    for i in range(itterations):
        # Perturb phi and psi
        rand_residue = random.uniform()
        rand_residue = int(rand_residue * N_residues +1)
        phi_pert = random.gaussian()
        psi_pert = random.gaussian()
        orig_phi = pose.phi(rand_residue)
        orig_psi = pose.psi(rand_residue)
        pose.set_phi(rand_residue, orig_phi + phi_pert)
        pose.set_psi(rand_residue, orig_psi + psi_pert)
        
        #add packing and minimization calls to 
        tf = core.pack.task.TaskFactory()
        task = tf.create_task_and_apply_taskoperations(pose)
        task.restrict_to_repacking()
        core.pack.pack_rotamers(pose, sxfn, task)

        minimizer.run(pose, movemap, sxfn, min_opts)
        mc.boltzmann(pose)
        
        sum_score += pose.energies().total_energy()
        
        if mc.mc_accepted_string().startswith("accepted"):
            accepted +=1

    acceptance_rate = accepted/itterations
    avg_score = sum_score/itterations
        
    print(f"Acceptance rate: {acceptance_rate}")
    print(f"Average score: {avg_score}")

    print(f"Score: {sxfn.score(pose)}")
    print(f"Score of lowest scoirng pose: {sxfn.score(mc.lowest_score_pose())}")
    


def main():
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

    #the_observer = moves.AddPyMOLObserver(mypose)
    #the_observer.pymol().apply(mypose)
    
    #instantiate fold tree
    fold_tree = fold_tree_from_ss(mypose)
    assert fold_tree.check_fold_tree(), "FoldTree is invalid"
    # Some builds encode N; if present, sanity check against pose size
    try:
        assert fold_tree.nres() == mypose.total_residue()
    except AttributeError:
        pass  # not all builds expose nres()

    mypose.fold_tree(fold_tree)
    
    mc_loop(pose=mypose, sxfn=sxfn)
    
if __name__ == "__main__":
    main()
#mypose.dump_pdb("Output.pdb")


"""
Acceptance rate: 0.6285714285714286
Average score: -245.06445169069838
Score: -247.56247117578533
Score of lowest scoirng pose: -247.56247117578533
"""