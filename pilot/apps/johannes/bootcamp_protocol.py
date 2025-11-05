from pyrosetta import *
from pyrosetta.rosetta.core.kinematics import FoldTree
from pyrosetta.rosetta.core.scoring.dssp import Dssp

import argparse

def fold_tree_from_ss(pose) -> FoldTree:
    dssp = Dssp(pose)
    secstruct = dssp.get_dssp_secstruct()
    ft = fold_tree_from_dssp_string(secstruct)
    return ft

def get_middles(elements_list):
    sec_segments_middles = [] #describes every other secondary structure mid point, still  need the loop mid point
    for seg in elements_list: # get middle of first secondary structure
        a,b = seg
        mid = (a + b)//2
        sec_segments_middles.append(mid)
    return sec_segments_middles


def fold_tree_from_dssp_string(ss):
    ft = FoldTree()
    segments = identify_secondary_structure_spans(ss)
    if not segments:
        return ft

    # ----- compute loop spans between adjacent segments -----
    loop_spans = []
    for (l0, r0), (l1, r1) in zip(segments, segments[1:]):
        loop_start = r0 + 1
        loop_end = l1 - 1
        if loop_start <= loop_end:
            loop_spans.append((loop_start, loop_end))

    # After the last range
    end = segments[-1][1]

    sec_middles = get_middles(segments)
    loop_middles = get_middles(loop_spans)

    # jump edges
    root = sec_middles[0]
    jump_targets = [mid for mid in sec_middles[1:]] + [mid for mid in loop_middles]
    jump_targets_sorted = sorted(jump_targets, key=lambda x: abs(x - root))
    jump_edges = [(root, mid, i) for i, mid in enumerate(jump_targets_sorted, start=1)]

    # normal edges
    normal_edges = []

    # For each segment, connect its middle to its left and right boundaries
    for i, ((start, end), middle) in enumerate(zip(segments, sec_middles)):
        
        # Nterm start
        left = 1 if i == 0 else start
        right = len(ss) if i == len(segments) - 1 else end
                # Ctermn end

        normal_edges.append((middle, left, -1))
        normal_edges.append((middle, right, -1))

    # For each loop, connect its middle to the start and end of the loop
    for (start, end), middle in zip(loop_spans, loop_middles):
        normal_edges.append((middle, start, -1))
        normal_edges.append((middle, end, -1))

    all_edges = jump_edges + normal_edges
    all_edges.sort(key=lambda x: (x[0], x[1], x[2]))

    # add to FoldTree
    for start, end,  label in all_edges:
        ft.add_edge(start, end, label)


    return ft


def identify_secondary_structure_spans(input_string: str) -> list:
    result: list = []
    i = 0
    n = len(input_string)

    while i < n:
        ch = input_string[i]
        if ch in ('H', 'E'):
            start = i + 1
            i += 1
            while i < n and input_string[i] == ch:
                i += 1
            result.append((start, i))
        else:
            i += 1

    return result

if __name__ == "__main__":
    init(extra_options="-ignore_unrecognized_res")

    parser = argparse.ArgumentParser()
    #add line here to add an argument
    parser.add_argument('filename')
    args = parser.parse_args()
    file = args.filename

    mypose = pose_from_pdb(file)
    ft = fold_tree_from_ss(pose=mypose)
    print(dir(ft))
    print(ft.size())

