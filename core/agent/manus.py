from lazyllm import pipeline, bind, Color, ChatPrompter
from lazyllm.tools.agent.functionCall import StreamResponse

from core.tools import (
    plan2md, 
    set_task_to_worker,
    get_more_info_from_user
)
from core.agent.agent import CustomReactAgent
from core.prompt.planner_prompt import MANUS_PLAN_INSTRUCTION
from core.prompt.solver_prompt import MANUS_SOLVER_INSTRUCTION


class Manus():
    PLAN_PROMPT = MANUS_PLAN_INSTRUCTION
    SOLVE_SYSTEM_PROMPT = MANUS_SOLVER_INSTRUCTION

    def __init__(self, plan_llm, solve_llm, max_retries: int = 5, return_trace: bool = False, stream: bool = False):
        self._max_retries = max_retries
        self._plan_llm = plan_llm.share(prompt=ChatPrompter(instruction=self.PLAN_PROMPT))
        self._solve_llm = solve_llm.share()
        self._tools = ["set_task_to_worker", "get_more_info_from_user"]
        self._return_trace = return_trace
        self._stream = stream
        self._build_agent_ppl()
        
    def _build_agent_ppl(self):
        with pipeline() as self._agent:
            self._agent.plan_ins = StreamResponse(prefix="[Planner 🤔] Receive instruction:", prefix_color=Color.yellow, color=Color.magenta, stream=True)
            self._agent.planner = self._plan_llm
            self._agent.plan_out = StreamResponse(prefix="[Planner 🤔] Todo List created:", prefix_color=Color.yellow, color=Color.magenta, stream=True)
            self._agent.parse = plan2md | bind(query=self._agent.input)
            self._agent.solver = CustomReactAgent(
                llm=self._solve_llm.share(),
                tools=self._tools,
                custom_prompt=self.SOLVE_SYSTEM_PROMPT,
                max_retries=self._max_retries,
                return_trace=self._return_trace,
                stream=self._stream
            )

    def forward(self, query: str):
        return self._agent(query)
    
    def __call__(self, query: str):
        return self._agent(query)
