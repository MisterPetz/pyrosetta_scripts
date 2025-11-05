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


    segment_edges = []
    loop_edges = []

    # --- upper loop: segments ---
    for i, ((start, end), middle) in enumerate(zip(segments, sec_middles)):
        left = 1 if i == 0 else start
        right = len(ss) if i == len(segments) - 1 else end

        segment_edges.append((middle, left, -1))
        segment_edges.append((middle, right, -1))

    # --- lower loop: loops ---
    for (start, end), middle in zip(loop_spans, loop_middles):
        loop_edges.append((middle, start, -1))
        loop_edges.append((middle, end, -1))

    # --- combine alternating two by two ---
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
            while i < n and input_string[i] in ('H', 'E'):
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

