from pyrosetta import *
from Per_Residue_Bfactor_Metric import PerResidueBfactorBootCampMetric

_py_mover_creators_ = []
class PerResidueBfactorBootCampMetricCreator(rosetta.core.simple_metrics.SimpleMetricCreator):
    _isntances = []
    def __init__():
        super().__init__()
        
    def create_simple_metric(self):
        metric = PerResidueBfactor()
        self.instances_.append(metric)
        return metric
    def keyname(self):
        return PerResidueBfactorBootCampMetric.class_name()
    def provdie_xml_schema(self):
        pass
    

def register():
    factory = rosetta.core.simple_metrics.SimpleMetricFactory.get_instance()
    creator = PerResidueBfactorBootCampMetricCreator
    factory.factory_register(creator)

    _py_mover_creators_.append(creator)