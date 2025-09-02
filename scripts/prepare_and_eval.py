"""
Number predictions with question IDs and evaluate using evaluator.py.

Data layout (as requested):
- Questions: tests/raw/questions.txt         # lines like "12345. question text"
- Predictions: tests/raw/prediction.txt      # lines like "사실형,부정,과거,확실"
- Answers (gold): tests/raw/answers.txt      # lines like "12345. 사실형,부정,과거,확실"

Outputs:
- tests/processed/prediction_numbered.txt
- tests/processed/score_report.txt

Run:
  python scripts/prepare_and_eval.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Ensure project root on sys.path to import src modules
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.evaluator import ResponseEvaluator  # noqa: E402


QUESTIONS = Path("tests/raw/questions.txt")
PREDICTIONS = Path("tests/raw/prediction.txt")
ANSWERS = Path("tests/raw/answers.txt")
OUT_DIR = Path("tests/processed")
OUT_PRED = OUT_DIR / "prediction_numbered.txt"
OUT_REPORT = OUT_DIR / "score_report.txt"
MAX_WRONG_EXAMPLES = 10

ID_PATTERN = re.compile(r"^(\d+)\.")


def read_nonempty_lines(p: Path) -> list[str]:
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def extract_ids(lines: list[str]) -> list[str]:
    ids: list[str] = []
    for s in lines:
        m = ID_PATTERN.match(s)
        if m:
            ids.append(m.group(1))
    return ids


def number_predictions(q_ids: list[str], preds: list[str]) -> list[str]:
    n = min(len(q_ids), len(preds))
    return [f"{q_ids[i]}. {preds[i]}" for i in range(n)]


def main() -> None:
    # Validate inputs
    for p in (QUESTIONS, PREDICTIONS, ANSWERS):
        if not p.exists():
            raise SystemExit(f"파일 없음: {p}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    q_lines = read_nonempty_lines(QUESTIONS)
    p_lines = read_nonempty_lines(PREDICTIONS)
    ids = extract_ids(q_lines)
    if not ids:
        raise SystemExit("questions.txt에서 유효한 번호를 찾지 못했습니다. '12345. ...' 형식 필요")

    numbered = number_predictions(ids, p_lines)
    OUT_PRED.write_text("\n".join(numbered) + "\n", encoding="utf-8")

    # Evaluate using evaluator.py (no API calls needed)
    # Call with output_file=None to get results and customize report (limit wrong samples).
    evaluator = ResponseEvaluator(gpt_client=None)  # type: ignore[arg-type]
    results = evaluator.evaluate_from_files(str(ANSWERS), str(OUT_PRED), None)

    # Build a compact report with up to MAX_WRONG_EXAMPLES wrong samples
    if "error" in results:
        report_lines = [
            "===== 채점 결과 =====",
            results["error"],
            f"정답만 존재: {results.get('gold_only', [])} | 예측만 존재: {results.get('pred_only', [])}",
        ]
    else:
        report_lines = [
            "===== 채점 결과 =====",
            f"시각: {results['timestamp']}",
            f"샘플 수(교집합): {results['total_samples']}",
            f"정답만 존재: {results['gold_only']} | 예측만 존재: {results['pred_only']}",
        ]
        for attr, acc in results["slot_accuracy"].items():
            report_lines.append(f"{attr}: {acc:.4f}")
        report_lines.extend([
            f"전체 평균 점수(4속성 평균): {results['overall_average']:.4f}",
            f"(참고) exact match: {results['exact_match']:.4f}",
            f"오답 수: {results['wrong_count']}",
        ])

        wrong_samples = results.get("wrong_samples") or []
        if wrong_samples:
            report_lines.append(
                f"===== 오답 상세 (예시 {min(MAX_WRONG_EXAMPLES, len(wrong_samples))}개) ====="
            )
            for idx, g, p in wrong_samples[:MAX_WRONG_EXAMPLES]:
                report_lines.append(f"{idx}. 정답: {g} | 예측: {p}")
            if len(wrong_samples) > MAX_WRONG_EXAMPLES:
                report_lines.append(
                    f"... (총 {results['wrong_count']}개 중 {MAX_WRONG_EXAMPLES}개 표시)"
                )

    OUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Saved numbered predictions to: {OUT_PRED}")
    print(f"Saved evaluation report to: {OUT_REPORT}")


if __name__ == "__main__":
    main()
