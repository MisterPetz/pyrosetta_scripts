from pyrosetta import *
from pyrosetta.rosetta import core, std
from pyrosetta.rosetta.core import select
from pyrosetta.rosetta.std import map_unsigned_long_double

class PerResidueBfactorBootCampMetric(rosetta.core.simple_metrics.PerResidueRealMetric):
    _clones = list()
    def __init__(self, atom_type = None):
        super().__init__()
        self._atom_type = atom_type
        
        
    @staticmethod
    def class_name() -> str:
        return "PerResidueBfactorBootCampMetric"
    
    def name(self) -> str:
        pass
    
    def clone(self):
        copy = PerResidueBfactorBootCampMetric()
        copy.atom_type_ = self.atom_type_
        PerResidueBfactorBootCampMetric.clones_.append(copy)
        return copy
    
    def parse_my_tag(self, tag, datamap):
        if tag.hasOption("atom_type"):
            self._atom_type = tag.get_option_string("atom_type", 1)
    
    def metric(self):
        return "bfactor"
    
    @classmethod
    def provide_xml_schema(cls, xsd):
        from pyrosetta.rosetta.utility.tag import XMLSchemaAttribute, XMLSchemaType
        from pyrosetta.rosetta.utility.tag import xs_string

        attrlist = std.list_utility_tag_XMLSchemaAttribute_t()

        attrlist.append(XMLSchemaAttribute.required_attribute(
                "atom_type",
                XMLSchemaType(xs_string),
                "String atom type"))

        description = "Per-residue B-factor metric for a specified atom name. plddt"
        core.simple_metrics.xsd_simple_metric_type_definition_w_attributes(
                xsd,
                cls.class_name(),
                description, attrlist)
        
    def calculate(self, pose):
        residue_selector = self.get_selector()
        subset = residue_selector.apply(pose)
        selection = select.get_residues_from_subset(subset)

        pdb_info = pose.pdb_info()

        b_fact_map = map_unsigned_long_double()
        
        for resi in selection:
           rt = pose.residue_type(resi)
           if rt.has(self.atom_type_):

               atom_idx = rt.atom_index(self.atom_type_)
               b_fact_map[ int(resi) ] = float(pdb_info.bfactor(resi, atom_idx))
        return b_fact_map


