import logging
from typing import Iterator, Optional

from . import bot as _bot
from .report import Report
from .report_type import ReportType
get_bot_client = _bot.get_bot_client
BotResults = _bot.BotResults
Prompt = _bot.Prompt
PropertyDefinition = _bot.PropertyDefinition
PropertyType = _bot.PropertyType
Image = _bot.Image

def run_bot(prompt : Prompt, config : dict = {}, logger : Optional[logging.Logger] = None) -> BotResults:
    """
    Run the report bot with the given prompt.
    :param prompt: Prompt for bot.
    :param config: Bot client configuration.
    :param logger: Optional logger.
    """
    return get_bot_client(config.get("bot_client", "openai"), config, logger).run(prompt)

def run_report(report_type : ReportType, config : dict = {}, logger : Optional[logging.Logger] = None) -> Iterator[Report]:
    """
    Run report bot with prompt from given report type, keep generating new reports as long as `ReportType:next`
    returns a `ReportType` instance. Return an iterator where each iteration is the next report in the chain.
    
    :param report_type: Report type of report to generate.
    :param config: Bot client configuration.
    :param logger: Optional logger.
    """
    report_values = {}
    current_report_type : Optional[ReportType] = report_type
    while current_report_type:
        if logger: logger.info("Run report type '%s'." % current_report_type.name, extra={"prompt": current_report_type.prompt.to_dict()})
        bot_results = run_bot(current_report_type.prompt, config, logger)
        report = Report(current_report_type, bot_results)
        yield report
        report_values[report.type.name] = report.values
        current_report_type = current_report_type.next(report_values)