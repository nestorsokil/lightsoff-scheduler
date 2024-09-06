import anthropic
import logging
import json
from datetime import datetime, timedelta
import csv
import io


def ocr_image_to_calendar_api_multi(image_b64):
    text = _ocr_image(
        image_b64, 'I uploaded an image of a power outage schedule table which shows hours of the day across the top and group numbers in 1st column. The image may be split into 2 12-hour sub-tables. Orange cells indicate outage periods. The date is highlighted at the top. Combine consecutive outage periods into single events. Only respond with a valid minified json of format {"group": [[full datetime start, full datetime end],[full datetime start, full datetime end]]}, then add a separator "->" and date in format "%Y-%m-%d".')
    logging.debug("Received text from OCR: %s", text)
    parts = text.split("->")
    return json.loads(parts[0].strip()), datetime.strptime(parts[1].strip(), "%Y-%m-%d")


def ocr_image_to_timeframes(image_b64):
    text = _ocr_image(
        image_b64, 'Don\'t interpret the image text. Turn the large green-orange table into CSV, use 0 for orange, 1 for green, add headers, no prompt, add separator "FOR_DATE:" and date %Y-%m-%d from the top of the image.')
    logging.info("Received text from OCR: %s", text)
    parts = text.split("FOR_DATE:")
    day = datetime.strptime(parts[1].strip(), "%Y-%m-%d")
    csv_string = parts[0].strip()
    csv_reader = csv.reader(io.StringIO(csv_string))

    result = {}
    next(csv_reader, None)  # skip the headers
    for row in csv_reader:
        group = row[0]
        result[group] = []
        for i, cell in enumerate(row[1:]):
            if cell == "0":
                start = day + timedelta(hours=i)
                end = day + timedelta(hours=i + 1)
                if i != 0 and len(result[group]) > 0 and result[group][-1] is not None and result[group][-1][1] == start:
                    result[group][-1][1] = end
                else:
                    result[group].append([start, end])
    return result, day


def mock_ocr_to_calendar_api_multi():
    text = '{"1.1":[["2024-09-05T00:00:00","2024-09-05T01:00:00"],["2024-09-05T11:00:00","2024-09-05T14:00:00"]],"1.2":[["2024-09-05T05:00:00","2024-09-05T07:00:00"],["2024-09-05T19:00:00","2024-09-05T21:00:00"]],"2.1":[["2024-09-05T07:00:00","2024-09-05T09:00:00"],["2024-09-05T21:00:00","2024-09-05T23:00:00"]],"2.2":[["2024-09-05T10:00:00","2024-09-05T12:00:00"],["2024-09-05T23:00:00","2024-09-06T01:00:00"]],"3.1":[["2024-09-05T01:00:00","2024-09-05T03:00:00"],["2024-09-05T14:00:00","2024-09-05T16:00:00"]],"3.2":[["2024-09-05T03:00:00","2024-09-05T05:00:00"],["2024-09-05T17:00:00","2024-09-05T19:00:00"]]}->2024-09-05'
    parts = text.split("->")
    return json.loads(parts[0].strip()), datetime.strptime(parts[1].strip(), "%Y-%m-%d")


def _ocr_image(image_b64, prompt):
    client = anthropic.Anthropic()  # defaults to os.environ.get("ANTHROPIC_API_KEY)
    logging.info("Sending image to Anthropics API for OCR...")
    message = client.messages.create(
        max_tokens=1000,
        temperature=0,
        system=prompt,
        model="claude-3-5-sonnet-20240620",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": str(image_b64)
                        }
                    }
                ]
            }
        ]
    )
    logging.info("Received response from Anthropics API.")
    return message.content[0].text
