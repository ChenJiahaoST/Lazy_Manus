import time

from lazyllm import OnlineChatModule, ThreadPoolExecutor, FileSystemQueue, LOG
from lazyllm.tools import fc_register, MCPClient
from core.prompt.solver_prompt import MANUS_WORKER_INSTRUCTION
from core.agent.agent import CustomReactAgent
from core.tools.utils import get_mcp_server_config
from core.tools import (
    web_search,
    python_executor,
)


def get_worker_tools(worker_type: str, allowed_tools: list=None):
    config = get_mcp_server_config({
        'Search': 'remote_playwright',
        'Git': 'github',
        'FileManager': 'filesystem',
        'Map': 'amap'
    }[worker_type])
    client = MCPClient(command_or_url=config.get('command') or config.get('url'), args=config.get('args'), env=config.get("env"))
    return client.get_tools(allowed_tools=allowed_tools)


@fc_register("tool")
def set_task_to_worker(target_worker: str, task: str, aim: str, want: str, task_path: str=None):
    """
    用于给某一特定worker分配任务，以实现你的特定目标。worker的具体类型如下：
    - Search：具备网络搜索、网页浏览的能力，可以根据给定主题搜索内容，并返回具体的搜索信息（你可以要求返回内容中包含具体网址等额外信息）。
    - Code：擅长编写代码（python、html、css等），内置python代码执行器，能够调试Python程序。
    - Git：具备代码仓库管理的能力，能够连接github，搜索相关功能的代码仓库，同时支持创建新的代码仓库，并把写好的代码上传至github（需要提供具体代码）。
    - FileManager：文件管理器，能够实现路径下的文件操作，例如创建、删除、查找等。
    - Map：提供地图工具，能够根据给定的位置信息规划行程（支持各种交通工具），同时支持查询具体位置的天气状况。
    
    Args:
        target_worker (str): 在可选择范围内选择一个类型的worker，可选范围是['Search', 'Git', 'Code', 'FileManager', 'Map']
        task (str): 任务描述，用于描述你的任务是什么。
        aim (str): 任务目标，介绍任务用于达到什么目的。
        want (str): 期望结果，明确你希望worker输出什么内容，例如具体信息、生成文件并提供文件路径、输出代码与测试结果等。
        task_path(str, optional): 提供本次任务的工程根目录路径。
    """
    try:
        worker_config = {
            'Search': lambda: ['web_search'] \
                + get_worker_tools('Search') \
                + get_worker_tools(
                    'FileManager',
                    ["list_allowed_directories", "list_directory", "edit_file", "write_file", "read_file"]
                ),
            'Git': lambda: get_worker_tools('Git'),
            'FileManager': lambda: get_worker_tools('FileManager'),
            'Map': lambda: get_worker_tools('Map') \
                + get_worker_tools(
                    'FileManager',
                    ["list_allowed_directories", "list_directory", "edit_file", "write_file", "read_file"]
                ),
            'Code': lambda: ['python_executor'] \
                + get_worker_tools(
                    'FileManager',
                    ["list_allowed_directories", "list_directory", "edit_file", "write_file", "read_file"]
                )
        }
        
        if target_worker not in worker_config:
            return f"当前类型不支持，可选范围是{list(worker_config.keys())}"
        
        task_info = f"任务描述：{task}\n任务目标：{aim}\n期望结果：{want}"
        if task_path:
            task_info += f"\n\n任务目录路径：{task_path}"
        
        tools = worker_config[target_worker]()
    except Exception as e:
        LOG.error(f"Fail to init {target_worker} worker, error: {e}")
        raise Exception(f"Fail to init {target_worker} worker, error: {e}")
    try:
        with ThreadPoolExecutor(1) as executor:
            worker = CustomReactAgent(
                llm=OnlineChatModule(source="deepseek", stream=True),
                tools=tools,
                custom_prompt=MANUS_WORKER_INSTRUCTION,
                max_retries=10,
                stream=True
            )
            future = executor.submit(worker, task_info)
            while True:
                if value := FileSystemQueue().dequeue():
                    print("".join(value))
                elif future.done():
                    break
                else:
                    time.sleep(0.3)
            final_result = future.result()
        return final_result
    except Exception as e:
        return f"Meet exception when worker process task\nYou can try again"
    

