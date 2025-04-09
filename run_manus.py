import time
from dotenv import load_dotenv

load_dotenv()

import lazyllm
from lazyllm import OnlineChatModule, FileSystemQueue, ThreadPoolExecutor

from core.agent.manus import Manus


def main():
    question = input("Hi, I'm Lazy Manus!\nPlease enter your task：\n")
    try:
        lazyllm.globals._init_sid()
        with ThreadPoolExecutor(1) as executor:
            agent = Manus(
                plan_llm=OnlineChatModule(source="deepseek", stream=True),
                solve_llm=OnlineChatModule(source="deepseek", stream=True),
                return_trace=True,
                stream=True,
                max_retries=30
            )
            future = executor.submit(agent, question)
            while True:
                if value := FileSystemQueue().dequeue():
                    print("".join(value))
                elif future.done():
                    break
                else:
                    time.sleep(0.3)
    except KeyboardInterrupt as e:
        raise e

if __name__ == "__main__":
    main()