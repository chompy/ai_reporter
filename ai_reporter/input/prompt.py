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
        output_properties : Iterable[PropertyDefinition],
        system_prompt : str = DEFAULT_SYSTEM_PROMPT,
        images : list[Image] = [],
        tools : dict[str,dict] = {},
        model : str = "gpt-4o-mini",
        max_iteration_prompt : str = DEFAULT_MAX_ITERATION_PROMPT,
        max_iterations : int = 5,
        max_error_retry : int = 3
    ):
        self.user_prompt = user_prompt
        self.output_properties = output_properties
        self.system_prompt = system_prompt
        self.images = images
        self.model = model
        self.max_iteration_prompt = max_iteration_prompt
        self.max_iterations = max_iterations
        self.max_error_retry = max_error_retry
        self.tools = tools
