from lazyllm import LOG
from lazyllm.tools import fc_register


@fc_register("tool")
def get_more_info_from_user(prompt: str) -> str:
    """
    该工具用于反问用户，以获取更多有效信息。当你认为有必要主动询问用户时，使用这个工具。

    Args:
        prompt (str): Markdown formatted prompt which contains your understanding of the task, the current state, and a series of questions you want to ask to the user.
    """
    LOG.info("Now I think I need more information from you...")
    LOG.info(prompt)
    res = input("Please provide more information: ")
    return res



    