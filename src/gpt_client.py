"""GPT API와 통신하기 위한 클라이언트 모듈"""
import openai


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
