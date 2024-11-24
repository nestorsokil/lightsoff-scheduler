import os
import anthropic
import logging
import json
from datetime import date

prompt = """
Read message potentially talking about power outage. 
Return JSON map of ISO day -> boolean if there will be outages. Empty map if nothing related in text.
"""

def detect(text):
    if os.environ.get("ANTHROPIC_API_KEY") is None:
        logging.debug("ANTHROPIC_API_KEY is not set")
        return {}

    logging.info("Sending message to Anthropics API")
    client = anthropic.Anthropic()  # defaults to os.environ.get("ANTHROPIC_API_KEY")
    message = client.messages.create(
        max_tokens=1000,
        temperature=0,
        system=prompt,
        model="claude-3-5-sonnet-20240620",
        messages=[{"role": "user", "content": text}])
    result = message.content[0].text
    if result is None or result == "":
        return {}
    parsed_data = {}
    data = json.loads(result)
    for key in data.keys():
        parsed_data[date.fromisoformat(key)] = data[key]
    return parsed_data
