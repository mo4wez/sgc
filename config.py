import os
import json
from pathlib import Path
from dotenv import load_dotenv
from exceptions import InvalidJsonConfigFileException


class SamawebGradeCheckerConfig:
    def __init__(self):
        try:
            self.term, self.login_url, self.refresh_rate = self._read_config()
            self.api_id, self.api_hash, self.token, self.username, self.password = self._read_env_config()
        except InvalidJsonConfigFileException:
            exit(2)

    def _read_env_config(self):
        load_dotenv(verbose=False)
        env_path = Path('./env') / '.env'
        load_dotenv(dotenv_path=str(env_path))

        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        token = os.getenv("TOKEN")
        username = os.getenv("USER_NAME")
        password = os.getenv("PASSWORD")

        return api_id, api_hash, token, username, password

    def _read_config(self):
        with open('config.json') as f:
            data = json.load(f)

        if 'term_no' not in data:
            raise InvalidJsonConfigFileException('term_no')
        if 'sama_login_url' not in data:
            raise InvalidJsonConfigFileException('sama_login_url')
        if 'refresh_rate' not in data:
            raise InvalidJsonConfigFileException('refresh_rate')

        return data['term_no'], data['sama_login_url'], data['refresh_rate']