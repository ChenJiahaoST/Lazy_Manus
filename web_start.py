from dotenv import load_dotenv

load_dotenv()

from lazyllm import OnlineChatModule, WebModule

from core.agent.manus import Manus


if __name__ == "__main__":
    agent = Manus(
        plan_llm=OnlineChatModule(source="deepseek", stream=True),
        solve_llm=OnlineChatModule(source="deepseek", stream=True),
        return_trace=True,
        stream=True,
        max_retries=30
    )
    w = WebModule(agent, stream=True)
    w.start().wait()