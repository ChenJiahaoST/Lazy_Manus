import json


def json_list_parser(text: str) -> list:
    """
    提取完整目录
    """
    try:
        # 找到第一个 '[' 和最后一个 ']' 的索引
        start_index = text.rfind('[')
        end_index = text.rfind(']')
        if start_index == -1 or end_index == -1:
            # 没有找到有效的 JSON 结构，返回空列表
            return []
        json_str = text[start_index:end_index+1]
        # 尝试解析 JSON
        data = json.loads(json_str)
        return data
    except Exception as e:
        # 如果解析出错，输出错误信息并返回空列表
        print("解析 JSON 出错:", e)
        raise e


def plan2md(text: str, query: str=None) -> str:
    todo_list = json_list_parser(text)
    if query:
        plan_str = f"任务：{query}\nTODO List:\n"
    else:
        plan_str = "TODO List:\n"
    for step in todo_list:
        step_str = f"- [ ] {step['step']}\n      {step['desc']}\n\n"
        plan_str += step_str
    return plan_str


def get_mcp_server_config(server_name):
    with open("./mcp_config_list.json", "r") as f:
        config = json.load(f)
    return config['mcpServers'][server_name]
