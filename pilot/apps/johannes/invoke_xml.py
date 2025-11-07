import argparse
from pyrosetta import *
from pyrosetta import pose_from_file
from pyrosetta.rosetta.protocols.rosetta_scripts import XmlObjects
import register_mover


EMBEDDED_XML = """<ROSETTASCRIPTS>
  <SCOREFXNS>
    <ScoreFunction name="sfxn" weights="ref2015"/>
  </SCOREFXNS>
  <MOVERS>
    <BootCampMover name="bm" num_iterations="20" scorefxn="sfxn"/>
  </MOVERS>
  <PROTOCOLS>
    <Add mover_name="bm"/>
  </PROTOCOLS>
</ROSETTASCRIPTS>
"""


register_mover.register()

init(extra_options="-ignore_unrecognized_res")

parser = argparse.ArgumentParser()


parser.add_argument('filename')
args = parser.parse_args()


pose = pose_from_file(args.filename)


xmlobj = XmlObjects.create_from_string(EMBEDDED_XML)
protocol = xmlobj.get_mover("ParsedProtocol")
protocol.apply(pose)


print("BootCampMoverPy applied successfully!")
