from typing import List

from lazyllm.tools.agent import ReactAgent
from lazyllm.tools.agent.functionCall import FunctionCall
from lazyllm.module import ModuleBase
from lazyllm import loop


class CustomReactAgent(ReactAgent):
    """
    继承自lazyllm.tools.agent.ReactAgent
    添加自定义提示词、agent流式输出
    """
    #  继承的目的只是为了自定义提示词。。。
    def __init__(self, llm, tools: List[str], custom_prompt: str, max_retries: int = 5, return_trace: bool = False, stream: bool = False):
        # 先调用父类的基础检查和属性设置（如果有必要可以直接调用 ModuleBase.__init__）
        ModuleBase.__init__(self, return_trace=return_trace)
        self._max_retries = max_retries
        assert llm and tools, "llm and tools cannot be empty."
        # 使用自定义的 prompt 来构造 _agent
        self._agent = loop(
            FunctionCall(llm, tools, _prompt=custom_prompt, return_trace=return_trace, stream=stream),
            stop_condition=lambda x: isinstance(x, str),
            count=self._max_retries
        )
