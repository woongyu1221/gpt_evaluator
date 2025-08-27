"""
GPT API와 통신하기 위한 클라이언트 모듈
"""
from typing import Dict, Any
import openai

class GPTClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def get_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        GPT API에 프롬프트를 보내고 응답을 받는 메서드
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response
        except Exception as e:
            raise Exception(f"GPT API 호출 중 오류 발생: {str(e)}")
