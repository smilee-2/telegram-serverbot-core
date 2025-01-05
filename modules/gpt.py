from g4f.client import Client
from g4f.Provider import RetryProvider, DDG, Mhystical, Blackbox, DarkAI, GizAI
import g4f.debug
import asyncio
from queue import Queue

#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
q = Queue()

# Отправка запроса в gpt. Если нейросеть не ответит, спросят следующую по списку
def request(msg: str) -> str:
    q.put(msg)
    g4f.debug.logging = True
    g4f.debug.version_check = False

    client = Client(
        provider=RetryProvider([DDG, Blackbox, GizAI, Mhystical, DarkAI], shuffle=False)
    )

    response = client.chat.completions.create(
        model="",
        messages=[
            {
                "role": "user",
                "content": q.get() + f". Отвечай только на русском языке"
            }
        ]
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content
