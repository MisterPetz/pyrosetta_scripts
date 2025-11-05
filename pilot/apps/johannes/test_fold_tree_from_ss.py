import pytest

from bootcamp_protocol import fold_tree_from_dssp_string

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


ss1 = "   EEEEE   HHHHHHHH  EEEEE   IGNOR EEEEEE   HHHHHHHHHHH  EEEEE  HHHH   "
expected1 = [(4, 8), (12, 19), (22, 26), (36, 41), (45, 55), (58, 62), (65, 68)]

ss2 = "HHHHHHH   HHHHHHHHHHHH      HHHHHHHHHHHHEEEEEEEEEEHHHHHHH EEEEHHH "
expected2 = [(1, 7), (11, 22), (29, 40), (41, 50), (51, 57), (59, 62), (63, 65)]

ss3 = "EEEEEEEEE EEEEEEEE EEEEEEEEE H EEEEE H H H EEEEEEEE"
expected3 = [(1, 9), (11, 18), (20, 28), (30, 30), (32, 36), (38, 38), (40, 40), (42, 42), (44, 51)]


@pytest.mark.parametrize(
    "input_string,expected",
    [
        pytest.param(ss1, expected1, id="mixed E/H with spaces and noise"),
        pytest.param(ss2, expected2, id="multiple H/E segments"),
        pytest.param(ss3, expected3, id="singletons and groups"),
    ],
)
def test_identify_secondary_structure_spans(input_string, expected):
    assert identify_secondary_structure_spans(input_string) == expected



