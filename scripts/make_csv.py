# make_q_and_a_from_userprompt_output.py
import csv, re
import os
from pathlib import Path

# 프로젝트 루트 디렉토리 설정
PROJECT_ROOT = Path(__file__).parent.parent

# 입출력 파일 경로 설정
INPUT = PROJECT_ROOT / "data" / "raw" / "test_case.csv"
Q_OUT = PROJECT_ROOT / "data" / "processed" / "test_questions.txt"
A_OUT = PROJECT_ROOT / "data" / "processed" / "test_answers.txt"

def read_rows(path):
    for enc in ("utf-8-sig","utf-8","cp949","euc-kr"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except Exception:
            pass
    raise RuntimeError("CSV 읽기 실패")

def main():
    # 디렉토리가 없으면 생성
    Q_OUT.parent.mkdir(parents=True, exist_ok=True)
    
    rows = read_rows(INPUT)
    headers = rows[0].keys()

    text_col = "user_prompt" if "user_prompt" in headers else next(iter(headers))
    labels_col = "output" if "output" in headers else None

    with open(Q_OUT, "w", encoding="utf-8") as fq:
        for i, r in enumerate(rows, 1):
            fq.write(f"{i}.{(r.get(text_col,'') or '').strip()}\n")

    if labels_col:
        with open(A_OUT, "w", encoding="utf-8") as fa:
            for i, r in enumerate(rows, 1):
                lab = (r.get(labels_col,"") or "").strip().strip('"').strip("'")
                lab = re.sub(r"\s+","", lab)
                fa.write(f"{i}. {lab}\n")

if __name__ == "__main__":
    main()
