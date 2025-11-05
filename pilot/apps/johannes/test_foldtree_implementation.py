import pytest

from bootcamp_protocol import fold_tree_from_dssp_string


def identify_secondary_structure_spans(input_string: str) -> list:
    # create fold tree
    ft = fold_tree_from_dssp_string(input_string)
    parts = ft.to_string().split("EDGE")[1:]


    # for each part, take the next 3 numbers and convert to int
    edges = [list(map(int, p.split()[:3])) for p in parts]
    result = [(i[0], i[1]) for i in edges]

    
    return result

def test_tree_size():
    ft = fold_tree_from_dssp_string(ss)
    assert ft.size() == 38
    
    
 
ss = "   EEEEEEE    EEEEEEE         EEEEEEEEE    EEEEEEEEEE   HHHHHH         EEEEEEEEE         EEEEE     "

EXPECTED_EDGES = [
    (7, 1), (7, 10), (7, 12), (12, 11),
    (12, 14), (7, 18), (18, 15), (18, 21),
    (7, 26), (26, 22), (26, 30), (7, 35),
    (35, 31), (35, 39), (7, 41), (41, 40),
    (41, 43), (7, 48), (48, 44), (48, 53),
    (7, 55), (55, 54), (55, 56), (7, 59),
    (59, 57), (59, 62), (7, 67), (67, 63),
    (67, 71), (7, 76), (76, 72), (76, 80),
    (7, 85), (85, 81), (85, 89), (7, 92),
    (92, 90), (92, 99)
]


@pytest.mark.parametrize(
    "input_string,expected",
    [
        pytest.param(ss, EXPECTED_EDGES, id="test"),
    ],
)
def test_identify_secondary_structure_spans(input_string, expected):
    assert identify_secondary_structure_spans(input_string) == expected



