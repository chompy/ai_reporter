# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from ai_reporter.bot import client as _client
from ai_reporter.bot import image as _image
from ai_reporter.bot import prompt as _prompt
from ai_reporter.bot import property as _property
from ai_reporter.bot import results as _results

get_bot_client = _client.get_bot_client
Prompt = _prompt.Prompt
PropertyDefinition = _property.PropertyDefinition
PropertyType = _property.PropertyType
Image = _image.Image
BotResults = _results.BotResults
