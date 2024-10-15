from ai_reporter.bot.property import PropertyDefinition, PropertyType
from ai_reporter.bot.tools.handler import ToolHandler
from ai_reporter.bot.tools.response import ToolDoneResponse
from ai_reporter.error.bot import MalformedBotResponseError


def test_done_tool():
    props = [
        PropertyDefinition("name", description="Person's name.", required=True),
        PropertyDefinition("age", description="Person's age.", type=PropertyType.INT),
    ]
    tool_handler = ToolHandler({"done": {"properties": props}})
    resp = tool_handler.call("done", {"name": "Fake Person", "age": 30})
    assert isinstance(resp, ToolDoneResponse)
    assert resp.values.get("name") == "Fake Person"
    assert resp.values.get("age") == 30


def test_done_required():
    props = [
        PropertyDefinition("name", description="Person's name.", required=True),
        PropertyDefinition("age", description="Person's age.", type=PropertyType.INT),
    ]
    tool_handler = ToolHandler({"done": {"properties": props}})
    try:
        tool_handler.call("done", {"age": 30})
    except MalformedBotResponseError:
        assert True
