# GPT Response Evaluator

GPT API를 사용하여 질문에 대한 답변을 자동으로 평가하는 프로젝트입니다.

## 프로젝트 구조

```
gpt_evaluator/
├── src/                   # 소스 코드
│   ├── __init__.py
│   ├── gpt_client.py     # GPT API 통신 처리
│   ├── evaluator.py      # 답변 평가 로직
│   └── config.py         # 설정 관리
├── scripts/              # 유틸리티 스크립트
│   ├── make_csv.py              # 원본 CSV를 질문/정답 파일로 변환
│   ├── run_gpt_tests.py         # 무작위 테스트 세트 실행 (GPT 호출)
│   └── prepare_and_eval.py      # 로컬 예측 번호 매핑 + 평가 (오프라인)
├── config/               # 설정 파일
│   ├── config.json       # 평가 기준 설정
│   └── system_prompt.txt # 기본 시스템 프롬프트
├── tests/                # 로컬 평가용 샘플 데이터
│   ├── raw/              # 원본 질문·예측·정답 텍스트
│   └── processed/        # 번호 매핑된 예측 및 리포트 출력
└── data/                 # 데이터 저장 디렉토리 (대규모 실험)
    ├── raw/              # 원본 CSV 등
    ├── processed/        # 질문·정답 텍스트
    └── results/          # GPT 결과 및 보고서
```

## 주요 컴포넌트

### GPTClient (`src/gpt_client.py`)
- OpenAI GPT API와의 통신을 담당
- `gpt-4o` 모델을 사용하며 시스템 프롬프트와 질문을 전달해 답변을 생성
- API 호출 및 응답 처리
- 기본 `temperature`는 0.4이며 필요 시 `get_response` 호출 인자로 조정 가능
- `run_test_sets(...)`는 무작위로 질문 묶음을 만들고, 응답/정답/리포트를 `data/results/<타임스탬프>/`에 저장

### ResponseEvaluator (`src/evaluator.py`)
- 파일 기반 평가: `'번호. 라벨1,라벨2,라벨3,라벨4'` 형식을 파싱하여 슬롯 정확도/Exact Match 계산
- 속성 이름: `유형, 극성, 시제, 확실성`
- 리포트 저장: 요약 지표와 오답(일부 샘플) 출력

### Config (`src/config.py`)
- 설정 파일 로드 및 관리
- `.env`에서 API 키 로드 및 평가 기준 제공

## 설정

프로젝트 루트에 `.env` 파일을 생성하고 OpenAI API 키를 설정합니다:

```
OPENAI_API_KEY=your-api-key-here
```

`config/config.json` 파일은 GPT에게 평가 프롬프트를 만들 때 사용할 일반적 기준(설명용)을 담습니다. 파일 기반 채점에는 직접 사용되지 않습니다:

```json
{
    "evaluation_criteria": {
        "relevance": "답변이 질문과 얼마나 관련이 있는지",
        "accuracy": "제공된 정보의 정확성",
        "completeness": "답변이 질문의 모든 측면을 다루었는지",
        "clarity": "답변이 명확하고 이해하기 쉬운지"
    }
}
```

## 시작하기

1. 프로젝트 클론
```bash
git clone [repository-url]
cd gpt_evaluator
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
- 프로젝트 루트에 `.env` 파일을 생성하여 OpenAI API 키 저장

4. (옵션) CSV 데이터 전처리
```bash
python scripts/make_csv.py
```
- `data/raw/test_case.csv`을 읽어 `data/processed/test_questions.txt`,
  `data/processed/test_answers.txt`를 생성합니다.

5. 사용 예시 (Python)
```python
from src.config import Config
from src.gpt_client import GPTClient
from src.evaluator import ResponseEvaluator

# 설정 로드
config = Config("config/config.json")

# GPT 클라이언트 초기화
gpt_client = GPTClient(config.get_api_key())

# 시스템 프롬프트와 질문을 이용한 직접 호출
answer = gpt_client.get_response(
    question="2+2는?",
    system_prompt="당신은 수학을 잘하는 친절한 도우미입니다.",
    temperature=0.4,  # 기본값은 0.4이며 필요 시 조절 가능
)

# 평가기 초기화
evaluator = ResponseEvaluator(gpt_client)

# 답변 평가
result = evaluator.evaluate_response(
    question="당신의 질문",
    response="평가할 답변",
    criteria=config.get_evaluation_criteria()
)
```

### 명령줄 실행 (GPT 호출 기반)

데이터를 준비한 뒤에는 다음 스크립트들로 전체 과정을 실행할 수 있습니다.

```bash
# 질문·정답 텍스트 생성 (data/raw/test_case.csv 필요)
python scripts/make_csv.py

# 무작위 테스트 세트에 대해 GPT 분류 및 평가 실행
python scripts/run_gpt_tests.py
```

`run_gpt_tests.py`는 `config/system_prompt.txt`에 저장된 시스템 프롬프트와 기본값을 사용합니다. 필요한 경우 `--set-size`, `--set-count`, `--question-file`, `--answer-file`, `--output-dir` 등을 조정할 수 있습니다.

### 로컬 오프라인 평가 (tests/raw → tests/processed)

GPT 호출 없이, 이미 생성된 예측을 질문 번호에 맞춰 붙이고 정답과 비교하여 채점할 수 있습니다. 다음 레이아웃을 사용하세요:

- `tests/raw/questions.txt`    예: `12345. 질문 내용`
- `tests/raw/prediction.txt`   예: `사실형,부정,과거,확실`
- `tests/raw/answers.txt`      예: `12345. 사실형,부정,과거,확실`

실행:

```bash
python scripts/prepare_and_eval.py
```

출력:

- `tests/processed/prediction_numbered.txt`  → 예측에 번호가 매겨진 파일 `"번호. 라벨1,라벨2,라벨3,라벨4"`
- `tests/processed/score_report.txt`         → 요약 지표와 오답 예시 리포트

동작 요약:
- `questions.txt`에서 상단부터 번호를 추출하여 `prediction.txt` 각 줄 앞에 순서대로 부여
- `answers.txt`와 교집합 번호만 채점 대상
- 오답 상세는 예시 10개만 표시하며, 스크립트 내 `MAX_WRONG_EXAMPLES`로 조정 가능

## 확장 가능성

- 추가 평가 기준 구현
- 웹 인터페이스 추가
- 결과 저장 및 분석 기능
- 다양한 GPT 모델 지원
- 배치 프로세싱 지원

### 빠른 실행
```bash
#라이브러리 다운
pip install -r requirements.txt

# 질문·정답 텍스트 생성 (data/raw/test_case.csv 필요)
python scripts/make_csv.py

# 무작위 테스트 세트에 대해 GPT 분류 및 평가 실행 (결과는 data/results/<타임스탬프>/ 저장)
python scripts/run_gpt_tests.py  # 필요 시 --set-size, --set-count 등 옵션 지정

# 오프라인: tests/raw → 번호 매핑 및 채점 결과를 tests/processed 에 저장
python scripts/prepare_and_eval.py

```
