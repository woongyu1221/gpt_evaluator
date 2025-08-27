"""GPT API와 통신하기 위한 클라이언트 모듈"""

imp    def run_test_sets(
        self,
        question_file: str,
        set_size: int,
        set_count: int,
        output_dir: str,
        system_prompt: str = "",
        answer_file: Optional[str] = None,
        evaluator: Optional["ResponseEvaluator"] = None,
        **kwargs,
    ) -> None:
        """테스트 세트를 생성하고 실행"""
        results_list = []  # 평가 결과를 저장할 리스트import random
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI

from .evaluator import ResponseEvaluator


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
        evaluator: Optional["ResponseEvaluator"] = None,  # 평가기 파라미터 추가
        **kwargs,
    ) -> None:
        """`test_questions.txt`에서 무작위 테스트 세트를 생성하고 GPT 응답을 저장"""
        q_path = Path(question_file)
        if not q_path.exists():
            raise FileNotFoundError(f"질문 파일을 찾을 수 없습니다: {question_file}")

        # 번호와 질문을 함께 파싱
        questions = []
        q_pat = re.compile(r"^\s*(\d+)\.\s*(.*)$")
        with q_path.open(encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                mo = q_pat.match(s)
                if mo:
                    idx = int(mo.group(1))
                    text = mo.group(2).strip()
                    questions.append((idx, text))
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

        total_questions = len(questions)
        if set_size > total_questions:
            raise ValueError(
                f"요청한 set_size {set_size}가 전체 질문 수 {total_questions}보다 큽니다"
            )
        for i in range(set_count):
            # Generate unique random indices within the full question range.
            # If duplicates occur, keep drawing until the requested size is met.
            indices = set()
            while len(indices) < set_size:
                idx = random.randrange(total_questions)
                if 0 <= idx < total_questions:
                    indices.add(idx)

            indices = list(indices)
            random.shuffle(indices)
            sampled = [questions[j] for j in indices]

            # Create a prompt using the original question numbers so that
            # numbering is consistent with the source files.
            prompt = "\n".join(f"{idx}. {q}" for idx, q in sampled)
            response = self.get_response(prompt, system_prompt, **kwargs)

            # Save the question set with the original numbering
            q_file = out_dir / f"questions_set_{i+1}.txt"
            q_file.write_text(prompt, encoding="utf-8")

            # Post-process GPT response to ensure numbering matches the
            # sampled questions. We rely on the order of the responses
            # corresponding to the order of the questions.
            pred_lines = []
            resp_lines = [
                line.strip() for line in response.splitlines() if line.strip()
            ]
            for (idx, _), line in zip(sampled, resp_lines):
                if "." in line:
                    _, line = line.split(".", 1)
                pred_lines.append(f"{idx}. {line.strip()}")

            pred_file = out_dir / f"predictions_set_{i+1}.txt"
            pred_file.write_text("\n".join(pred_lines), encoding="utf-8")

            if answers and evaluator:
                gold_lines = []
                for idx, _ in sampled:
                    if idx in answers:
                        gold_lines.append(f"{idx}. {','.join(answers[idx])}")
                gold_file = out_dir / f"gold_set_{i+1}.txt"
                gold_file.write_text("\n".join(gold_lines), encoding="utf-8")

                # 평가 수행
                result = evaluator.evaluate_from_files(
                    str(gold_file),
                    str(pred_file),
                    str(out_dir / f"score_report_set_{i+1}.txt")
                )
                result = evaluator.evaluate_from_files(
                    str(gold_file), str(pred_file), str(report_file)
                )
                results_list.append(result)

        if results_list:
            summary_file = out_dir / "score_report_summary.txt"
            with summary_file.open("w", encoding="utf-8") as f:
                for idx, res in enumerate(results_list, 1):
                    f.write(f"===== 세트 {idx} =====\n")
                    f.write(f"샘플 수: {res['total_samples']}\n")
                    for attr in evaluator.ATTRS:
                        f.write(f"{attr}: {res['slot_accuracy'][attr]:.4f}\n")
                    f.write(
                        f"전체 평균 점수(4속성 평균): {res['overall_average']:.4f}\n"
                    )
                    f.write(f"(참고) exact match: {res['exact_match']:.4f}\n\n")

                total_samples = sum(r["total_samples"] for r in results_list)
                slot_totals = {attr: 0.0 for attr in evaluator.ATTRS}
                exact_total = 0.0
                for r in results_list:
                    exact_total += r["exact_match"] * r["total_samples"]
                    for attr in evaluator.ATTRS:
                        slot_totals[attr] += r["slot_accuracy"][attr] * r["total_samples"]

                if total_samples:
                    f.write("===== 전체 합산 =====\n")
                    slot_avgs = {
                        attr: slot_totals[attr] / total_samples for attr in evaluator.ATTRS
                    }
                    for attr, acc in slot_avgs.items():
                        f.write(f"{attr}: {acc:.4f}\n")
                    overall_avg = sum(slot_avgs.values()) / len(slot_avgs)
                    exact_avg = exact_total / total_samples
                    f.write(
                        f"전체 평균 점수(4속성 평균): {overall_avg:.4f}\n"
                    )
                    f.write(f"(참고) exact match: {exact_avg:.4f}\n")
