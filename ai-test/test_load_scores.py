import csv
from pathlib import Path
import runpy
import sys

import pytest

from load_scores import load_scores

ROOT = Path(__file__).resolve().parent


def make_csv(tmp_path, rows):
    path = tmp_path / "sample.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "score"])
        writer.writerows(rows)
    return path


def test_정상_파일을_읽는다():
    kept, skipped = load_scores(ROOT / "scores.csv")
    assert kept == [
        ("김하나", 88), ("최,네번", 77), ("김하나", 91),
        ("윤보람", 64), ("서한별", 95),
    ]
    assert [row[0] for row in skipped] == [3, 4, 7, 8, 9]


def test_빈_줄은_기록없이_건너뛴다(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text("name,score\n\n김하나,88\n\n", encoding="utf-8")
    assert load_scores(path) == ([("김하나", 88)], [])


def test_이름에_쉼표가_있어도_읽는다(tmp_path):
    path = make_csv(tmp_path, [["최,네번", 77]])
    assert load_scores(path) == ([("최,네번", 77)], [])


def test_없는_파일이면_오류가_난다(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "없는파일.csv")


def test_헤더만_있으면_빈_결과가_나온다():
    assert load_scores(ROOT / "empty.csv") == ([], [])


@pytest.mark.parametrize("score, valid", [
    (-1, False), (0, True), (1, True),
    (99, True), (100, True), (101, False),
])
def test_점수_경계값(tmp_path, score, valid):
    path = make_csv(tmp_path, [["경계", score]])
    kept, skipped = load_scores(path)
    if valid:
        assert kept == [("경계", score)]
        assert skipped == []
    else:
        assert kept == []
        assert skipped == [(2, f"경계,{score}", "점수가 0~100 밖")]


def test_빈_이름을_거르고_이유를_기록한다(tmp_path):
    path = make_csv(tmp_path, [["   ", 90]])
    assert load_scores(path) == ([], [(2, "   ,90", "이름이 비어 있음")])


@pytest.mark.parametrize("row, original", [
    (["김하나"], "김하나"),
    (["김하나", "88", "비고"], "김하나,88,비고"),
])
def test_열_개수가_다르면_기록한다(tmp_path, row, original):
    path = make_csv(tmp_path, [row])
    assert load_scores(path) == ([], [(2, original, "열 개수가 2가 아님")])


@pytest.mark.parametrize("raw, reason", [
    ("", "점수가 비어 있음"),
    ("결석", "점수가 정수가 아님"),
    ("88.5", "점수가 정수가 아님"),
    ("7 2", "점수가 정수가 아님"),
])
def test_유효하지_않은_점수를_기록한다(tmp_path, raw, reason):
    path = make_csv(tmp_path, [["학생", raw]])
    assert load_scores(path) == ([], [(2, f"학생,{raw}", reason)])


def test_같은_이름의_유효한_자료를_모두_남긴다(tmp_path):
    path = make_csv(tmp_path, [["김하나", 88], ["김하나", 91]])
    assert load_scores(path) == ([("김하나", 88), ("김하나", 91)], [])


def test_이름과_점수의_양끝_공백을_제거한다(tmp_path):
    path = make_csv(tmp_path, [["  한겨울  ", "  77  "]])
    assert load_scores(path) == ([("한겨울", 77)], [])


def test_weird_파일의_제외_기록을_확인한다():
    kept, skipped = load_scores(ROOT / "weird.csv")
    assert kept == [("한겨울", 77), ("윤보람", 88)]
    assert [row[0] for row in skipped] == [2, 3, 4, 5, 6, 7, 9]
    assert len(skipped) == 7
    assert all(reason for _, _, reason in skipped)


def test_입력_파일을_수정하지_않는다(tmp_path):
    path = make_csv(tmp_path, [["김하나", 88], ["오류", 101]])
    before = path.read_bytes()
    load_scores(path)
    assert path.read_bytes() == before


def test_명령행에서_파일명을_생략하면_scores를_읽는다(monkeypatch, capsys):
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(sys, "argv", ["load_scores.py"])
    runpy.run_path(str(ROOT / "load_scores.py"), run_name="__main__")
    output = capsys.readouterr().out
    assert "읽은 줄 : 5개" in output
    assert "건너뛴 줄 : 5개" in output
    assert "김하나 88" in output
    assert "점수가 0~100 밖" in output


def test_명령행에서_지정한_파일을_읽는다(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["load_scores.py", str(ROOT / "empty.csv")])
    runpy.run_path(str(ROOT / "load_scores.py"), run_name="__main__")
    assert capsys.readouterr().out == "읽은 줄 : 0개\n건너뛴 줄 : 0개\n"
