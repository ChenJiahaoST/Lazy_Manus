import traceback
from io import StringIO
from contextlib import redirect_stdout
from concurrent.futures import ProcessPoolExecutor, TimeoutError

from lazyllm.tools import fc_register

def run_code(code, safe_globals):
    """
    在安全环境中执行代码，并捕获输出。
    """
    try:
        with StringIO() as buf, redirect_stdout(buf):
            exec(code, safe_globals, safe_globals)
            output = buf.getvalue()
        return {"observation": output, "success": True}
    except Exception:
        return {"observation": traceback.format_exc(), "success": False}


@fc_register("tool")
def python_executor(code, timeout=5):
    """
    该工具用于执行 Python 代码，输出一个包含代码执行状态和输出/错误信息的字典，支持超时控制，注意请在代码中添加必要的import。
    
    Args:
        code (str): 要执行的 Python 代码字符串。
        timeout (int, optional): 执行超时时间（单位秒），默认5秒。
    """
    print("python executor is used")
    if isinstance(__builtins__, dict):
        builtins_copy = __builtins__.copy()
    else:
        builtins_copy = __builtins__.__dict__.copy()
    # 保持 __import__ 可用
    safe_globals = {"__builtins__": builtins_copy}
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_code, code, safe_globals)
        try:
            result = future.result(timeout=timeout)
        except TimeoutError:
            future.cancel()
            result = {"observation": f"Execution timeout after {timeout} seconds", "success": False}
    return result
