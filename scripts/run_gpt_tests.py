import argparse
from src.config import Config
from src.gpt_client import GPTClient


def main():
    parser = argparse.ArgumentParser(description="Run GPT classification on random test sets.")
    parser.add_argument("--question-file", default="data/processed/test_questions.txt")
    parser.add_argument("--set-size", type=int, required=True)
    parser.add_argument("--set-count", type=int, default=1)
    parser.add_argument("--output-dir", default="data/results")
    parser.add_argument("--system-prompt", default="각 질문에 대해 '번호. 유형1, 유형2, 유형3, 유형4' 형식으로 답변하세요.")
    parser.add_argument("--answer-file", default="data/processed/test_answers.txt")
    parser.add_argument("--config", default="config/config.json")
    args = parser.parse_args()

    cfg = Config(args.config)
    client = GPTClient(cfg.get_api_key())
    client.run_test_sets(
        question_file=args.question_file,
        set_size=args.set_size,
        set_count=args.set_count,
        output_dir=args.output_dir,
        system_prompt=args.system_prompt,
        answer_file=args.answer_file,
    )


if __name__ == "__main__":
    main()
