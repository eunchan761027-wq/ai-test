import csv
import pytest
from load_scores import load_scores


def write_csv(tmp_path, rows, encoding="utf-8-sig"):
    path = tmp_path / "scores.csv"
    with path.open("w", encoding=encoding, newline="") as f:
        csv.writer(f).writerows([["name", "score"], *rows])
    return path


def test_normal_rows(tmp_path):
    path = write_csv(tmp_path, [["가", 88], ["나", 64]])
    assert load_scores(path) == ([("가", 88), ("나", 64)], [])


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "missing.csv")


@pytest.mark.parametrize("text", ["", "name,score\n"])
def test_empty_inputs(tmp_path, text):
    path = tmp_path / "empty.csv"
    path.write_text(text, encoding="utf-8")
    assert load_scores(path) == ([], [])


@pytest.mark.parametrize("score", [0, 1, 99, 100])
def test_valid_boundaries(tmp_path, score):
    assert load_scores(write_csv(tmp_path, [["학생", score]])) == ([("학생", score)], [])


@pytest.mark.parametrize("score", [-1, 101])
def test_invalid_boundaries(tmp_path, score):
    path = write_csv(tmp_path, [["학생", score]])
    assert load_scores(path) == ([], [(2, f"학생,{score}", "점수가 0~100 밖")])


@pytest.mark.parametrize("value, reason", [
    ("", "점수가 비어 있음"),
    ("abc", "점수가 정수가 아님"),
    ("88.5", "점수가 정수가 아님"),
])
def test_invalid_score(tmp_path, value, reason):
    path = write_csv(tmp_path, [["학생", value]])
    assert load_scores(path) == ([], [(2, f"학생,{value}", reason)])


def test_blank_name(tmp_path):
    assert load_scores(write_csv(tmp_path, [[" ", 90]])) == ([], [(2, " ,90", "이름이 비어 있음")])


@pytest.mark.parametrize("row, original", [(["가"], "가"), (["가", "50", "x"], "가,50,x")])
def test_wrong_column_count(tmp_path, row, original):
    assert load_scores(write_csv(tmp_path, [row])) == ([], [(2, original, "열 개수가 2가 아님")])


def test_blank_line_not_recorded(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text("name,score\n\n가,80\n", encoding="utf-8")
    assert load_scores(path) == ([("가", 80)], [])


def test_quoted_comma(tmp_path):
    assert load_scores(write_csv(tmp_path, [["가,나", 50]])) == ([("가,나", 50)], [])


def test_duplicate_names_kept(tmp_path):
    path = write_csv(tmp_path, [["가", 80], ["가", 90]])
    assert load_scores(path) == ([("가", 80), ("가", 90)], [])


def test_whitespace(tmp_path):
    assert load_scores(write_csv(tmp_path, [[" 가 ", " 80 "]])) == ([("가", 80)], [])


def test_utf8_bom(tmp_path):
    path = write_csv(tmp_path, [["가", 80]], encoding="utf-8-sig")
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    assert load_scores(path) == ([("가", 80)], [])
