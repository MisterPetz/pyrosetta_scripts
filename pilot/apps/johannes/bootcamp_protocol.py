from pyrosetta import *
from pyrosetta.rosetta.core.kinematics import FoldTree
from pyrosetta.rosetta.protocols.loops import Loop
from pyrosetta.rosetta.core.scoring.dssp import Dssp
from pyrosetta.rosetta.core.pose import Pose
from dataclasses import dataclass
from typing import List

@dataclass
class _Built:
    ft: FoldTree
    loops: List[Loop]
    loop_for_residue: List[int]  # 1..N, values in 0..len(loops)

class FoldTreeFromSS:
    def __init__(self, pose: Pose, loop_left: int = 2, loop_right: int = 3): # so loop left and right are just edges for the loop itself. 
        
        self._pose = pose
        self._loop_left = loop_left
        self._loop_right = loop_right
        self._loops = None
        self._ft = self._fold_tree()
        
        

    def build(self) -> _Built:
        """Construct and return the FoldTree, loops, and loop mapping."""
        
        loop_for_residue = [self._loop_for_residue(i) for i in range(1, self._pose.total_residue()+1)] #1 indexed?
        loops = [self._loop(e - 1) for e in loop_for_residue]
        
        return _Built(ft=self._ft, loops=loops, loop_for_residue=loop_for_residue)
        
    def _fold_tree(self) -> FoldTree:
        dssp = Dssp(self._pose)
        secstruct = dssp.get_dssp_secstruct()
        ft = self._fold_tree_from_dssp_string(secstruct)
        return ft
        
    def _fold_tree_from_dssp_string(self, ss) -> FoldTree:
        ft = FoldTree()
        segments = self._identify_secondary_structure_spans(ss)
        if not segments:
            return ft

        # compute loop spans between adjacent segments
        loop_spans = []
        for (l0, r0), (l1, r1) in zip(segments, segments[1:]):
            loop_start = r0 + 1
            loop_end = l1 - 1
            if loop_start <= loop_end:
                loop_spans.append((loop_start, loop_end))

        # After the last range
        end = segments[-1][1]

        sec_middles = self._get_middles(segments)
        loop_middles = self._get_middles(loop_spans)

        # jump edges
        root = sec_middles[0]
        jump_targets = [mid for mid in sec_middles[1:]] + [mid for mid in loop_middles]
        jump_targets_sorted = sorted(jump_targets, key=lambda x: abs(x - root))
        jump_edges = [(root, mid, i) for i, mid in enumerate(jump_targets_sorted, start=1)]


        segment_edges = []
        loop_edges = []

        # upper loop: segments
        for i, ((start, end), middle) in enumerate(zip(segments, sec_middles)):
            left = 1 if i == 0 else start
            right = len(ss) if i == len(segments) - 1 else end

            segment_edges.append((middle, left, -1))
            segment_edges.append((middle, right, -1))

        # lower loop: loops
        for (start, end), middle in zip(loop_spans, loop_middles):
            loop_edges.append((middle, start, -1))
            loop_edges.append((middle, end, -1))

        # combine alternating two by two
        combined_edges = []
        seg_i = loop_i = 0

        while seg_i < len(segment_edges) or loop_i < len(loop_edges):
            # take two from segment_edges
            for _ in range(2):
                if seg_i < len(segment_edges):
                    combined_edges.append(segment_edges[seg_i])
                    seg_i += 1
            # take two from loop_edges
            for _ in range(2):
                if loop_i < len(loop_edges):
                    combined_edges.append(loop_edges[loop_i])
                    loop_i += 1

        all_edges = jump_edges + combined_edges
        all_edges.sort(key=lambda x: (x[0], x[1], x[2]))

        normal_i = jump_i = 0
        for i in range(len(all_edges)):
            # Pattern repeats every 3 edges: [normal, normal, jump]
            pattern_pos = i % 3

            if pattern_pos in (0, 1):  # two normal edges
                start, end, label = combined_edges[normal_i]
                normal_i += 1
            else:  # one jump edge
                start, end, label = jump_edges[jump_i]
                jump_i += 1

            ft.add_edge(start, end, label)
            
        self._init_loops(ft)
        
        return ft
    
    def _init_loops(self, ft):
        
        cuts = list(ft.cutpoints()) # defines with its length the amount of loops there are
        
        # create a loop list # cut edges are not allowed to overlap another cut
        
        loops = []
        for idx, cut in enumerate(cuts):
            lower_bound = cut - self._loop_left
            upper_bound = cut + self._loop_right

            # Only check the next cut if it exists
            if idx + 1 < len(cuts) and upper_bound >= cuts[idx + 1]:
                upper_bound = cuts[idx] - 1

            loops.append((lower_bound, upper_bound, cut))
        self._loops = loops
        
    

    def _loop(self, index: int) -> Loop:
        a,b,c = self._loops[index]
        return Loop(a,b,c)

    def _loop_for_residue(self, seqpos: int) -> int: #gives an entry to the index for the array above start, end, cutpoint (so the loop defines the to be closed cutpoint for the resiude provieded by this funciton)
        
        peptide_out = [e for e in self._ft.get_outgoing_edges(seqpos) if e.is_peptide()]
        
        if not self._ft.is_root(seqpos) and len(peptide_out) == 0:
            e = self._ft.get_residue_edge(seqpos)
            start, stop = e.start(), e.stop()
            
        elif len(peptide_out) > 1:
            start, stop, = peptide_out[1].start(), peptide_out[1].stop()
        else:
            start, stop, = peptide_out[0].start(), peptide_out[0].stop()
        if stop == self._pose.total_residue() or stop == 1:
            return 0
        else:
            closest_index = min(
            range(len(self._loops)), 
            key=lambda i: abs(self._loops[i][2] - stop) # stop used here as target to the closest cutpoint of loops 
        )

            # Convert to 1-based index
            one_based_index = closest_index + 1
            return one_based_index

        
    def _identify_secondary_structure_spans(self, input_string: str) -> list:
        result: list = []
        i = 0
        n = len(input_string)

        while i < n:
            ch = input_string[i]
            if ch in ('H', 'E'):
                start = i + 1
                i += 1
                while i < n and input_string[i] in ('H', 'E'):
                    i += 1
                result.append((start, i))
            else:
                i += 1

        return result
    
    def _get_middles(self, elements_list):
        sec_segments_middles = [] #describes every other secondary structure mid point, still  need the loop mid point
        for seg in elements_list: # get middle of first secondary structure
            a,b = seg
            mid = (a + b)//2
            sec_segments_middles.append(mid)
        return sec_segments_middles

if __name__ == "__main__":
    init(extra_options="-ignore_unrecognized_res")

    file = "1UBQ.pdb"
    mypose = pose_from_pdb(file)
    data = FoldTreeFromSS(mypose).build()
    idx = data.loop_for_residue[4]
    if idx > 0:
        ranloop = data.loops[idx]
        print(f"Closing loop: start={ranloop.start()} stop={ranloop.stop()} cut={ranloop.cut()}")
    

