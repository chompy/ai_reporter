from typing import Iterable
from .image import Image
from .property import PropertyDefinition

DEFAULT_SYSTEM_PROMPT = """
Using the tools available to you, perform an analysis of the user's message. Use the `done` tool to signal the completion of your analysis.
""".strip()

DEFAULT_MAX_ITERATION_PROMPT = """
Please complete your analysis now with the `done` tool. Explain what blockers you encountered (if any). If there were no blockers than please provide a summary of your findings.
"""

class Prompt:

    """ Contains data needed to prompt the AI model. """

    def __init__(
        self, 
        user_prompt : str,
        report_properties : Iterable[PropertyDefinition],
        system_prompt : str = DEFAULT_SYSTEM_PROMPT,
        images : list[Image] = [],
        tools : dict[str,dict] = {},
        model : str = "gpt-4o-mini",
        max_iterations : int = 5,
        max_error_retry : int = 3,
        max_iteration_prompt : str = DEFAULT_MAX_ITERATION_PROMPT
    ):

        """
        :param user_prompt: The query for the bot.
        :param report_properties: Definition of the values the bot should return.
        :param system_prompt: The parameters in which the bot should analyze the query.
        :param images: Images for the bot to analyze (in additional to the prompt).
        :param tools: The tools the bot is allowed to use and their configuration.
        :param model: The LLM to generate the report with.
        :param max_iterations: The maximum number of loops to take before forcing the bot to finish.
        :param max_error_retry: The maximum number of retries before giving up after the bot returns an erroneous response.
        :param max_iteration_prompt: The prompt to send to the bot when the maximum number of loops has been reached and it is forced to finish.
        """
        self.user_prompt = user_prompt
        self.report_properties = report_properties
        self.system_prompt = system_prompt
        self.images = images
        self.model = model
        self.max_iteration_prompt = max_iteration_prompt
        self.max_iterations = max_iterations
        self.max_error_retry = max_error_retry
        self.tools = tools

    def to_dict(self) -> dict:
        return {
            "user_prompt": self.user_prompt,
            "system_prompt": self.system_prompt,
            "images": list(map(lambda i: i.mime, self.images)),
            "tools": self.tools,
            "model": self.model,
            "max_iterations": self.max_iterations,
            "max_error_retry": self.max_error_retry,
            "max_iteration_prompt": self.max_iteration_prompt
        }