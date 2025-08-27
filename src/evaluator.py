"""
답변 평가를 위한 평가기 모듈
"""
import re
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple
from .gpt_client import GPTClient

class ResponseEvaluator:
    ATTRS = ["유형", "극성", "시제", "확실성"]

    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client

    def evaluate_response(self, question: str, response: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        주어진 질문과 응답에 대해 GPT 기반 평가를 수행하는 메서드
        """
        evaluation_prompt = self._create_evaluation_prompt(question, response, criteria)
        evaluation_result = self.gpt_client.get_response(evaluation_prompt)
        return self._parse_evaluation_result(evaluation_result)

    def evaluate_from_files(self, gold_file: str, pred_file: str, output_file: str = "score_report.txt") -> Dict[str, Any]:
        """
        파일에서 정답과 예측을 읽어와 평가를 수행하는 메서드
        """
        gold = self._parse_file(gold_file)
        pred = self._parse_file(pred_file)

        if not gold or not pred:
            return self._generate_empty_report(gold, pred)

        return self._evaluate_predictions(gold, pred, output_file)

    def _parse_file(self, path: str) -> Dict[int, List[str]]:
        """
        'N. 라벨1,라벨2,라벨3,라벨4' 형식의 파일을 파싱
        """
        m = {}
        pat = re.compile(r'^\s*(\d+)\.\s*(.+?)\s*$')
        with open(path, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                mo = pat.match(s)
                if not mo:
                    continue
                idx = int(mo.group(1))
                lab = mo.group(2).strip().strip('"').strip("'")
                lab = re.sub(r'\s+', '', lab)
                parts = lab.split(",")
                if len(parts) != 4:
                    continue
                m[idx] = parts
        return m

    def _evaluate_predictions(self, gold: Dict[int, List[str]], pred: Dict[int, List[str]], 
                            output_file: str) -> Dict[str, Any]:
        """
        예측 결과를 평가하고 결과를 파일에 저장
        """
        ids_gold = set(gold.keys())
        ids_pred = set(pred.keys())
        ids = sorted(ids_gold & ids_pred)

        if not ids:
            return self._generate_empty_report(gold, pred)

        total = len(ids)
        slot_correct = [0, 0, 0, 0]
        exact_correct = 0
        wrong = []

        for i in ids:
            g = gold[i]
            p = pred[i]
            exact = True
            for k in range(4):
                if p[k] == g[k]:
                    slot_correct[k] += 1
                else:
                    exact = False
            if exact:
                exact_correct += 1
            else:
                wrong.append((i, ",".join(g), ",".join(p)))

        results = self._calculate_metrics(total, slot_correct, exact_correct, 
                                       ids_gold, ids_pred, wrong)
        
        if output_file:
            self._save_report(results, output_file)

        return results

    def _calculate_metrics(self, total: int, slot_correct: List[int], 
                          exact_correct: int, ids_gold: Set[int], 
                          ids_pred: Set[int], wrong: List[Tuple]) -> Dict[str, Any]:
        """
        평가 지표 계산
        """
        slot_acc = [slot_correct[k] / total for k in range(4)]
        overall_avg = sum(slot_acc) / 4.0
        exact_match = exact_correct / total

        return {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_samples": total,
            "gold_only": len(ids_gold - ids_pred),
            "pred_only": len(ids_pred - ids_gold),
            "slot_accuracy": dict(zip(self.ATTRS, slot_acc)),
            "overall_average": overall_avg,
            "exact_match": exact_match,
            "wrong_count": len(wrong),
            "wrong_samples": wrong
        }

    def _generate_empty_report(self, gold: Dict[int, List[str]], 
                             pred: Dict[int, List[str]]) -> Dict[str, Any]:
        """
        평가할 수 없는 경우의 보고서 생성
        """
        return {
            "error": "공통 번호가 없어 채점할 수 없습니다.",
            "gold_only": sorted(set(gold.keys()) - set(pred.keys()))[:20],
            "pred_only": sorted(set(pred.keys()) - set(gold.keys()))[:20]
        }

    def _save_report(self, results: Dict[str, Any], output_file: str):
        """
        평가 결과를 파일로 저장
        """
        lines = [
            "===== 채점 결과 =====",
            f"시각: {results['timestamp']}",
            f"샘플 수(교집합): {results['total_samples']}",
            f"정답만 존재: {results['gold_only']} | 예측만 존재: {results['pred_only']}"
        ]

        for attr, acc in results['slot_accuracy'].items():
            lines.append(f"{attr}: {acc:.4f}")

        lines.extend([
            f"전체 평균 점수(4속성 평균): {results['overall_average']:.4f}",
            f"(참고) exact match: {results['exact_match']:.4f}",
            f"오답 수: {results['wrong_count']}"
        ])

        wrong_samples = results.get("wrong_samples")
        if wrong_samples:
            lines.append("===== 오답 상세 =====")
            for idx, g, p in wrong_samples:
                lines.append(f"{idx}. 정답: {g} | 예측: {p}")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _create_evaluation_prompt(self, question: str, response: str, criteria: Dict[str, Any]) -> str:
        """
        평가를 위한 프롬프트 생성
        """
        prompt = f"""
        다음 질문과 답변을 주어진 기준에 따라 평가해주세요:

        질문: {question}
        답변: {response}

        평가 기준:
        """
        for criterion, description in criteria.items():
            prompt += f"\n- {criterion}: {description}"
        
        return prompt

    def _parse_evaluation_result(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        GPT의 평가 결과를 파싱하여 구조화된 형태로 반환
        """
        return evaluation_result
