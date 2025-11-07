import argparse
from pyrosetta import *
from pyrosetta import pose_from_file
from pyrosetta.rosetta.protocols.rosetta_scripts import XmlObjects
import register_metric


# Embedded RosettaScripts XML:
EMBEDDED_XML = """<ROSETTASCRIPTS>
  <SCOREFXNS>
    <ScoreFunction name="sfxn" weights="ref2015"/>
  </SCOREFXNS>
  <SIMPLE_METRICS>
    <PerResidueBfactorBootCampMetric name="bfactor" atom_type="CA"/>
  </SIMPLE_METRICS>
  <MOVERS>
    <RunSimpleMetrics name="metrics" metrics="bfactor"/>
  </MOVERS>
  <PROTOCOLS>
    <Add mover="metrics"/>
  </PROTOCOLS>
</ROSETTASCRIPTS>
"""


register_metric.register()

init(extra_options="-ignore_unrecognized_res")

parser = argparse.ArgumentParser()


parser.add_argument('filename')
args = parser.parse_args()


pose = pose_from_file(args.filename)

xmlobj = XmlObjects.create_from_string(EMBEDDED_XML)
protocol = xmlobj.get_mover("ParsedProtocol")
protocol.apply(pose)


print("SimpleMetrics applied successfully!")
