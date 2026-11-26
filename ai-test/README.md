# 성적 CSV 검사 프로그램

## ① 무엇을 하나요 (What)

성적 CSV 파일을 읽어 이름이 있고 점수가 0~100 사이의 정수인 자료를 골라낸다. 유효한 자료는 `kept`에, 제외한 행의 번호·내용·이유는 `skipped`에 담아 반환한다.

## ② 왜 만들었나요 (Why)

성적 파일에는 빈 점수, 범위 밖 점수, 잘못된 열 개수 등이 섞여 있을 수 있다. 유효한 자료와 제외한 자료를 구분하는 동작을 테스트하고, 다른 사람도 실행할 수 있도록 사용 방법과 결과를 기록하는 것이 이 과제의 목적이다.

## ③ 어떻게 쓰나요 (How)

Python 3.11 이상을 사용한다. 아래 파일 10개를 같은 저장소 폴더에 넣고 그 폴더를 VS Code에서 연다. 터미널에서 다음 명령을 실행한다.

```bash
python -m pip install pytest==9.2.0 pytest-cov==7.1.0 coverage==7.17.5
python load_scores.py scores.csv
```

파일명을 생략한 `python load_scores.py`도 같은 폴더의 `scores.csv`를 읽는다. 다른 입력은 다음과 같이 지정한다.

```bash
python load_scores.py empty.csv
python load_scores.py weird.csv
```

| 입력 파일 | 유효한 자료 | 제외한 자료 |
| --- | ---: | ---: |
| `scores.csv` | 5개 | 5개 |
| `empty.csv` | 0개 | 0개 |
| `weird.csv` | 2개 | 7개 |

첫 행은 헤더로 건너뛰고, 빈 줄은 기록 없이 건너뛴다. 이름과 점수의 양끝 공백을 제거한다. 같은 이름의 유효한 자료는 모두 유지하며 소수 점수와 0~100 범위 밖 점수는 제외한다. 없는 파일을 지정하면 `FileNotFoundError`가 발생한다.

## ④ 어떻게 테스트하나요

```bash
# 설계표 기반 테스트
python -m pytest test_load_scores.py

# 줄 커버리지와 미실행 줄 확인
python -m pytest test_load_scores.py --cov=load_scores --cov-report=term-missing

# 세 테스트 파일 함께 실행
python -m pytest test_load_scores.py test_ai_A.py test_ai_B.py
```

Python 3.12.14, pytest 9.2.0, pytest-cov 7.1.0, coverage 7.17.5를 사용한 ChatGPT 작업 환경의 실제 결과이다.

| 테스트 파일 | 함수 수 | 매개변수별 실행 수 | 통과 | 전체 프로그램의 줄 커버리지 |
| --- | ---: | ---: | ---: | ---: |
| `test_load_scores.py` | 15 | 24 | 24 | 100% |
| `test_ai_A.py` | 13 | 21 | 21 | 80% |
| `test_ai_B.py` | 12 | 21 | 21 | 80% |

세 파일을 함께 실행하면 총 66개가 통과한다. 설계표 기반 테스트는 정상·예외·경계값 외에도 빈 이름, 열 개수, 중복 이름, 공백, 입력 파일 보존 및 명령행 실행을 확인한다. A와 B의 미실행 줄은 명령행 실행 부분인 77, 79~86행이다. 줄 커버리지 100%가 모든 입력에서의 정확성을 보장하지는 않는다.

**A/B 실험 상태:** 두 파일은 같은 대화에서 만든 비교용 예시다. 강의자료에서 요구한 동일 모델·설정의 독립된 새 대화 실험은 아직 수행하지 않았다. 제출 전 새 대화에서 받은 코드로 교체할 때는 코드를 수정하지 않은 채 실행하고 실제 결과로 위 표를 갱신한다.

## ⑤ 파일 구성

| 파일 | 역할 |
| --- | --- |
| `.gitignore` | Python 캐시 등 불필요한 파일을 Git 기록에서 제외 |
| `LICENSE` | 추가 작성한 테스트와 문서의 MIT License |
| `README.md` | 프로그램 설명, 실행 방법과 테스트 결과 |
| `load_scores.py` | 성적 CSV를 읽는 수업 배포 프로그램 |
| `scores.csv` | 정상 자료와 잘못된 자료가 섞인 입력 |
| `empty.csv` | 헤더만 있는 입력 |
| `weird.csv` | 빈 이름·빈 점수·소수 등 예외적인 입력 |
| `test_load_scores.py` | 설계표 기반 테스트와 보완 테스트 |
| `test_ai_A.py` | 코드 기반 AI 테스트 비교 예시 |
| `test_ai_B.py` | 명세 기반 AI 테스트 비교 예시 |

## ⑥ 만든 사람 · AI를 어디에 썼는지

- 만든 사람: 김은찬 / 학번: [학번 입력]
- AI를 쓴 곳: ChatGPT를 사용해 테스트 코드와 README를 작성하고 실행 결과를 확인했다. A/B는 독립된 새 대화의 결과가 아닌 비교 예시이다.
- 내가 직접 판단한 것: [직접 확인한 뒤 입력: 점수 경계값, 중복 이름을 유지하는 이유, AI가 제안한 기대값을 검토한 근거 등]

커밋의 Description에는 `Assisted-by: ChatGPT`를 기록한다.

### 자료 출처와 라이선스

한국기술교육대학교 AI 협업 프로그래밍 11주차 실습 「테스트코드 작성과 GitHub 문서화」를 참고했다. `load_scores.py`, 세 CSV와 `.gitignore`는 수업 배포 파일이며 원저작자와 기존 이용 조건을 유지한다. 추가 작성한 테스트와 문서는 [MIT License](LICENSE)를 따른다.

이 저장소의 파일 구성은 GitHub에 올릴 기본 10개 파일이다. 별도 과제 항목인 함정 실험, 워크시트, 짝 교차 검증과 소감은 함께 제공한 전체 과제 자료에서 진행한다.
