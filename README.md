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
├── tests/                # 테스트 코드
├── config/               # 설정 파일
│   └── config.json      # 평가 기준 설정
└── data/                # 데이터 저장 디렉토리
```

## 주요 컴포넌트

### GPTClient (`src/gpt_client.py`)
- OpenAI GPT API와의 통신을 담당
- `gpt-4o` 모델을 사용하며 시스템 프롬프트와 질문을 전달해 답변을 생성
- API 호출 및 응답 처리
- 에러 핸들링

### ResponseEvaluator (`src/evaluator.py`)
- 답변 평가 로직 구현
- 평가 프롬프트 생성
- 평가 결과 파싱 및 구조화

### Config (`src/config.py`)
- 설정 파일 로드 및 관리
- `.env`에서 API 키 로드 및 평가 기준 제공

## 설정

프로젝트 루트에 `.env` 파일을 생성하고 OpenAI API 키를 설정합니다:

```
OPENAI_API_KEY=your-api-key-here
```

`config/config.json` 파일에서는 평가 기준을 구성합니다:

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
pip install openai python-dotenv
```

3. 환경 변수 설정
- 프로젝트 루트에 `.env` 파일을 생성하여 OpenAI API 키 저장

4. 사용 예시
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

### 명령줄 실행

무작위 테스트 세트에 대해 GPT 분류를 실행하려면 아래 명령만으로 충분합니다.

```bash
python scripts/run_gpt_tests.py
```

`config/system_prompt.txt`에 저장된 시스템 프롬프트와 기타 기본값을 자동으로 사용하므로 별도의 인자를 전달할 필요가 없습니다. 필요한 경우 `--set-size` 등 인자를 직접 지정해 덮어쓸 수 있습니다.

## 확장 가능성

- 추가 평가 기준 구현
- 웹 인터페이스 추가
- 결과 저장 및 분석 기능
- 다양한 GPT 모델 지원
- 배치 프로세싱 지원
