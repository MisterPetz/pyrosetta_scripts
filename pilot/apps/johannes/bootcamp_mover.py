from pyrosetta import *
from pyrosetta.rosetta.numeric import random
from pyrosetta.rosetta.protocols import moves
from pyrosetta.rosetta import core
from bootcamp_protocol import fold_tree_from_ss
from pyrosetta.rosetta.core.scoring import parse_score_function
from pyrosetta.rosetta.core.scoring import get_score_function


# XSD stuff
from pyrosetta.rosetta.utility.tag import XMLSchemaType  
from pyrosetta.rosetta.protocols import moves
from pyrosetta.rosetta.core.scoring import (
    attributes_for_parse_score_function_w_description
)
# schema bits
from pyrosetta.rosetta.utility.tag import XMLSchemaAttribute, XMLSchemaType, XMLSchemaCommonType
from pyrosetta.rosetta.core.scoring import attributes_for_parse_score_function_w_description
from pyrosetta.rosetta.protocols import moves

class BootCampMover(pyrosetta.rosetta.protocols.moves.Mover):
    _clones = list()

    def __init__(self, sfxn = None, num_iterations: int = 500):
        super().__init__()
        self._sfxn = sfxn or get_score_function()
        self._num_iterations = num_iterations
    
    def get_num_itterations(self):
        return self._num_iterations#
    
    def set_num_itterations(self, num_iterations):
        self._num_iterations = num_iterations

    def set_sfxn(self, sfxn):
        self._sfxn = sfxn
        
    def get_sfxn(self):
        return self._sfxn
    
    def parse_my_tag(self, tag, datamap):
        if tag.hasOption("num_iterations"):
            iters = tag.get_option_int("num_iterations", 1)
            self.set_num_itterations(iters)
            
        self.set_sfxn(parse_score_function(tag, datamap))
    @staticmethod
    def get_name():
        return "BootCampMover"

    def clone(self):
        copy = BootCampMover(self._sfxn, self._num_iterations)
        BootCampMover._clones.append(copy)
        return copy

    def fresh_instance(self):
        return BootCampMover()
        
    def apply(self, pose):

        sfxn = self._sfxn
        # are these still needed?
        sfxn.set_weight(core.scoring.linear_chainbreak,1.0)
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
        mc = moves.MonteCarlo(pose, sfxn, 1.0)

        # Set up MoveMap for backbone and sidechain movement
        movemap = core.kinematics.MoveMap()
        movemap.set_bb(True)
        movemap.set_chi(True)
        # Minimizer setup
        min_opts = core.optimization.MinimizerOptions("lbfgs_armijo_atol", 0.01, True)
        minimizer = core.optimization.AtomTreeMinimizer()

        accepted = 0
        itterations = self._num_iterations
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
            core.pack.pack_rotamers(pose, sfxn, task)

            minimizer.run(pose, movemap, sfxn, min_opts)
            mc.boltzmann(pose)
            
            sum_score += pose.energies().total_energy()
            
            if mc.mc_accepted_string().startswith("accepted"):
                accepted +=1

        acceptance_rate = accepted/itterations
        avg_score = sum_score/itterations
            
        print(f"Acceptance rate: {acceptance_rate}")
        print(f"Average score: {avg_score}")

        print(f"Score: {sfxn.score(pose)}")
        print(f"Score of lowest scoirng pose: {sfxn.score(mc.lowest_score_pose())}")
    
    
    def provide_xml_schema(xsd):

        attrs = pyrosetta.rosetta.std.list_utility_tag_XMLSchemaAttribute_t()

        attrs.append(
            XMLSchemaAttribute.attribute_w_default(
                "num_iterations",
                XMLSchemaType(XMLSchemaCommonType.xsct_positive_integer),  # wrap it!
                "How many sampling iterations this mover will perform.",
                "10",
            )
        )
        
        attributes_for_parse_score_function_w_description(
            attrs, "ScoreFunction to use"
        )

        moves.xsd_type_definition_w_attributes(
            xsd,
            "BootCampMover",
            "BootCampMover: a simple example mover used in Boot Camp; "
            "supports 'num_iterations' and a custom ScoreFunction.",
            attrs
        )
        