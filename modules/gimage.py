import json
import time
import requests
import os
import base64
import random
from pathlib import Path
from queue import Queue

cwd = Path.cwd()
parent = cwd.parent
queue = Queue()

# Класс для генерации изображения. Нейросеть Kandinsky 3.1
class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self) -> int:
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt: str, model: int, images: int = 1, width: int = 1024, height: int = 1024) -> str:
        styles = ['KANDINSKY', 'UHD', 'ANIME', 'DEFAULT']
        params = {
            "type": "GENERATE",
            "numImages": images,
            "negativePromptUnclip": "3д дизайн, 3D изображение",
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id: str, attempts: int = 10, delay: int = 30) -> None | list[str]:
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

# Вызываемая функция для генерации
def generate_image(request, number, num_dir):
    queue.put(request)

    if not os.path.isdir(f'images/ImageBot{num_dir}'):
        os.makedirs(f'images/ImageBot{num_dir}', exist_ok=True)

    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', 'api','secret')
    model_id = api.get_model()
    uuid = api.generate(f"{queue.get()}", model_id)
    images = api.check_generation(uuid)

    with open(cwd / f"images/ImageBot{num_dir}/ImageGen{number}.png", "wb") as fh:
        fh.write(base64.decodebytes(images[0].encode(encoding="utf-8")))
