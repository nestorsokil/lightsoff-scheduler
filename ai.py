import anthropic
import logging
import csv
import io
import base64
from datetime import datetime, timedelta


# TODO unused
# Anthropics works correctly for this task only in 99% cases, it just HAS TO shift 1 event a day for 1 hours, stupid asshole
# GPT can't even format a proper CSV
def image_to_time_frames(image_bytes):
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
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
