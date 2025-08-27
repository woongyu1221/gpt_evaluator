"""GPT API와 통신하기 위한 클라이언트 모듈"""
import openai
import random
import re
from pathlib import Path
from typing import Optional
from openai import OpenAI

class GPTClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_response(
        self,
        question: str,
        system_prompt: str = "",
        temperature: float = 0.4,
        **kwargs,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})

        # 기본 temperature 값을 설정하되, 전달된 인자가 있으면 우선한다.
        kwargs.setdefault("temperature", temperature)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content

    def run_test_sets(
        self,
        question_file: str,
        set_size: int,
        set_count: int,
        output_dir: str,
        system_prompt: str = "",
        answer_file: Optional[str] = None,
        **kwargs,
    ) -> None:
        """`test_questions.txt`에서 무작위 테스트 세트를 생성하고 GPT 응답을 저장"""
        q_path = Path(question_file)
        if not q_path.exists():
            raise FileNotFoundError(f"질문 파일을 찾을 수 없습니다: {question_file}")

        # 번호와 질문을 함께 파싱
        questions = []
        with q_path.open(encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                if "." in s:
                    idx_part, text_part = s.split(".", 1)
                    try:
                        idx = int(idx_part.strip())
                    except ValueError:
                        continue
                    questions.append((idx, text_part.strip()))
                else:
                    questions.append((None, s))

        answers = {}
        if answer_file:
            a_path = Path(answer_file)
            if not a_path.exists():
                raise FileNotFoundError(f"정답 파일을 찾을 수 없습니다: {answer_file}")
            pat = re.compile(r"^\s*(\d+)\.\s*(.+?)\s*$")
            with a_path.open(encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        continue
                    mo = pat.match(s)
                    if not mo:
                        continue
                    idx = int(mo.group(1))
                    lab = mo.group(2).strip().strip('"').strip("'")
                    lab = re.sub(r"\s+", "", lab)
                    answers[idx] = lab.split(",")

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        for i in range(set_count):
            sampled = random.sample(questions, set_size)
            prompt = "\n".join(f"{idx}. {q}" for idx, q in sampled)
            response = self.get_response(prompt, system_prompt, **kwargs)
            q_file = out_dir / f"questions_set_{i+1}.txt"
            pred_file = out_dir / f"predictions_set_{i+1}.txt"
            q_file.write_text(prompt, encoding="utf-8")
            pred_file.write_text(response, encoding="utf-8")

            if answers:
                gold_lines = []
                for idx, _ in sampled:
                    if idx in answers:
                        gold_lines.append(f"{idx}. {','.join(answers[idx])}")
                gold_file = out_dir / f"gold_set_{i+1}.txt"
                gold_file.write_text("\n".join(gold_lines), encoding="utf-8")

                from .evaluator import ResponseEvaluator

                evaluator = ResponseEvaluator(self)
                report_file = out_dir / f"score_report_set_{i+1}.txt"
                evaluator.evaluate_from_files(
                    str(gold_file), str(pred_file), str(report_file)
                )
