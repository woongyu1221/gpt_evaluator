"""GPT API와 통신하기 위한 클라이언트 모듈"""
import openai
import random
from pathlib import Path


class GPTClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def get_response(self, question: str, system_prompt: str = "", **kwargs) -> str:
        """GPT-4o 모델에 시스템 프롬프트와 질문을 보내 답변을 반환"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": question})

            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                **kwargs,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"GPT API 호출 중 오류 발생: {str(e)}")

    def run_test_sets(
        self,
        question_file: str,
        set_size: int,
        set_count: int,
        output_dir: str,
        system_prompt: str = "",
        **kwargs,
    ) -> None:
        """`test_questions.txt`에서 무작위 테스트 세트를 생성하고 GPT 응답을 저장"""
        q_path = Path(question_file)
        if not q_path.exists():
            raise FileNotFoundError(f"질문 파일을 찾을 수 없습니다: {question_file}")

        with q_path.open(encoding="utf-8") as f:
            questions = [
                line.strip().split(".", 1)[1].strip()
                if "." in line else line.strip()
                for line in f
                if line.strip()
            ]

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        for i in range(set_count):
            sampled = random.sample(questions, set_size)
            prompt = "\n".join(f"{j+1}. {q}" for j, q in enumerate(sampled))
            response = self.get_response(prompt, system_prompt, **kwargs)
            (out_dir / f"questions_set_{i+1}.txt").write_text(prompt, encoding="utf-8")
            (out_dir / f"predictions_set_{i+1}.txt").write_text(response, encoding="utf-8")
