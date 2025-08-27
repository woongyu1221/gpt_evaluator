"""Utility script to run GPT classification on random test sets."""

import argparse
from pathlib import Path

from src.config import Config
from src.gpt_client import GPTClient


def _load_system_prompt(path: str) -> str:
    """Read the system prompt from ``path`` if it exists."""
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8").strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run GPT classification on random test sets."
    )
    parser.add_argument(
        "--question-file", default="data/processed/test_questions.txt"
    )
    parser.add_argument("--set-size", type=int, default=10)
    parser.add_argument("--set-count", type=int, default=1)
    parser.add_argument("--output-dir", default="data/results")
    parser.add_argument("--system-prompt", default=None)
    parser.add_argument(
        "--system-prompt-file", default="config/system_prompt.txt"
    )
    parser.add_argument("--answer-file", default="data/processed/test_answers.txt")
    parser.add_argument("--config", default="config/config.json")
    args = parser.parse_args()

    cfg = Config(args.config)
    system_prompt = args.system_prompt or _load_system_prompt(args.system_prompt_file)

    client = GPTClient(cfg.get_api_key())
    client.run_test_sets(
        question_file=args.question_file,
        set_size=args.set_size,
        set_count=args.set_count,
        output_dir=args.output_dir,
        system_prompt=system_prompt,
        answer_file=args.answer_file,
    )


if __name__ == "__main__":
    main()
