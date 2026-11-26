import csv
import pytest
from load_scores import load_scores


def data_file(tmp_path, rows):
    path = tmp_path / "input.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["name", "score"])
        writer.writerows(rows)
    return path


def test_valid_records_in_input_order(tmp_path):
    path = data_file(tmp_path, [["하나", 88], ["두리", 64]])
    assert load_scores(path) == ([("하나", 88), ("두리", 64)], [])


def test_duplicate_names_are_not_deleted(tmp_path):
    path = data_file(tmp_path, [["김하나", 88], ["김하나", 91]])
    assert load_scores(path) == ([("김하나", 88), ("김하나", 91)], [])


def test_comma_in_name(tmp_path):
    assert load_scores(data_file(tmp_path, [["최,네번", 77]])) == ([("최,네번", 77)], [])


def test_surrounding_whitespace(tmp_path):
    assert load_scores(data_file(tmp_path, [["  한겨울 ", " 77 "]])) == ([("한겨울", 77)], [])


def test_header_without_records(tmp_path):
    assert load_scores(data_file(tmp_path, [])) == ([], [])


def test_missing_path_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "does-not-exist.csv")


@pytest.mark.parametrize("score, accepted", [
    (-1, False), (0, True), (1, True), (99, True), (100, True), (101, False),
])
def test_score_limits(tmp_path, score, accepted):
    kept, skipped = load_scores(data_file(tmp_path, [["경계", score]]))
    assert kept == ([("경계", score)] if accepted else [])
    if accepted:
        assert skipped == []
    else:
        assert len(skipped) == 1
        assert skipped[0][0] == 2
        assert isinstance(skipped[0][1], str)
        assert skipped[0][2]


@pytest.mark.parametrize("raw", ["", "결석", "88.5", "7 2"])
def test_bad_score_is_reported(tmp_path, raw):
    kept, skipped = load_scores(data_file(tmp_path, [["학생", raw]]))
    assert kept == []
    assert len(skipped) == 1
    assert skipped[0][0] == 2
    assert skipped[0][2]


def test_empty_name_is_reported(tmp_path):
    kept, skipped = load_scores(data_file(tmp_path, [["", 90]]))
    assert kept == []
    assert len(skipped) == 1
    assert skipped[0][0] == 2
    assert skipped[0][2]


@pytest.mark.parametrize("row", [["학생"], ["학생", 90, "추가"]])
def test_wrong_number_of_columns(tmp_path, row):
    kept, skipped = load_scores(data_file(tmp_path, [row]))
    assert kept == []
    assert len(skipped) == 1
    assert skipped[0][0] == 2
    assert skipped[0][2]


def test_empty_lines_do_not_create_skip_records(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text("name,score\n\n학생,90\n\n", encoding="utf-8")
    assert load_scores(path) == ([("학생", 90)], [])


def test_input_file_remains_unchanged(tmp_path):
    path = data_file(tmp_path, [["학생", 50], ["오류", 101]])
    original = path.read_bytes()
    load_scores(path)
    assert path.read_bytes() == original
