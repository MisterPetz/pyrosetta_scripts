from pyrosetta import *
from abc import ABC, abstractmethod
import sys
import argparse
from pyrosetta import *
from pyrosetta.rosetta.numeric import random
from pyrosetta.rosetta.protocols import moves
from pyrosetta.rosetta import core
from bootcamp_protocol import fold_tree_from_ss

class BootCampMover(pyrosetta.rosetta.protocols.moves.Mover):
    def __init__(self):
        super().__init__(self) 
        
    @abstractmethod
    def apply(self, pose):

        sxfn = get_score_function()
        sxfn.set_weight(core.scoring.linear_chainbreak,1.0)
        #instantiate fold tree
        fold_tree = fold_tree_from_ss(pose)
        assert fold_tree.check_fold_tree(), "FoldTree is invalid"

        pose.fold_tree(fold_tree)
        cutpoints = [i for i in range(1, pose.size()) if fold_tree.is_cutpoint(i)]

        for k in cutpoints:
            core.pose.correctly_add_cutpoint_variants(pose, k)

        for k in cutpoints:
            assert pose.residue(k).has_variant_type(core.chemical.VariantType.CUTPOINT_LOWER)
            assert pose.residue(k+1).has_variant_type(core.chemical.VariantType.CUTPOINT_UPPER)
            
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
            
    @abstractmethod
    def get_name(self):
        return self.__class__.__name__
        