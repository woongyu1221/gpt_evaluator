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
│   └── config.json      # API 키 및 평가 기준 설정
└── data/                # 데이터 저장 디렉토리
```

## 주요 컴포넌트

### GPTClient (`src/gpt_client.py`)
- OpenAI GPT API와의 통신을 담당
- API 호출 및 응답 처리
- 에러 핸들링

### ResponseEvaluator (`src/evaluator.py`)
- 답변 평가 로직 구현
- 평가 프롬프트 생성
- 평가 결과 파싱 및 구조화

### Config (`src/config.py`)
- 설정 파일 로드 및 관리
- API 키 및 평가 기준 제공

## 설정

`config/config.json` 파일에서 다음 설정을 구성할 수 있습니다:

```json
{
    "api": {
        "openai_api_key": "your-api-key-here"
    },
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
pip install openai
```

3. 설정 파일 수정
- `config/config.json` 파일에서 OpenAI API 키 설정

4. 사용 예시
```python
from src.config import Config
from src.gpt_client import GPTClient
from src.evaluator import ResponseEvaluator

# 설정 로드
config = Config("config/config.json")

# GPT 클라이언트 초기화
gpt_client = GPTClient(config.get_api_key())

# 평가기 초기화
evaluator = ResponseEvaluator(gpt_client)

# 답변 평가
result = evaluator.evaluate_response(
    question="당신의 질문",
    response="평가할 답변",
    criteria=config.get_evaluation_criteria()
)
```

## 확장 가능성

- 추가 평가 기준 구현
- 웹 인터페이스 추가
- 결과 저장 및 분석 기능
- 다양한 GPT 모델 지원
- 배치 프로세싱 지원
