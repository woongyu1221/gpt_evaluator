import json
import os
from typing import Dict, Any

from dotenv import load_dotenv

class Config:
    def __init__(self, config_path: str):
        load_dotenv()
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        설정 파일 로드
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_api_key(self) -> str:
        """
        OpenAI API 키 반환
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return api_key
        return self.config.get('api', {}).get('openai_api_key', '')

    def get_evaluation_criteria(self) -> Dict[str, str]:
        """
        평가 기준 반환
        """
        return self.config['evaluation_criteria']
