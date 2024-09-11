import logging
import re
import pytesseract
from datetime import datetime, timedelta
from img2table.document import Image
from img2table.ocr import TesseractOCR
from PIL import Image as PILImage


def image_to_time_frames(image_path):
    try:
        image = Image(image_path, detect_rotation=False)

        logging.info("Extracting tables from image...")
        extracted_tables = image.extract_tables(
            ocr=TesseractOCR(n_threads=1, lang="ukr", psm=11),
            implicit_rows=False,
            implicit_columns=False,
            borderless_tables=False,
            min_confidence=1)
        logging.info(f"Extracted {len(extracted_tables)} tables from image.")

        if len(extracted_tables) == 0:
            logging.info("No tables found in the image.")
            text = pytesseract.image_to_string(PILImage.open(image_path), lang="ukr")
            return parse_non_table(text)

        pixels = PILImage.open(image_path).load()
        table = extracted_tables[0]
        day = extract_day(table)
        group_by_table_index = {
            1: "1.1", 2: "1.2", 3: "2.1", 4: "2.2", 5: "3.1", 6: "3.2",
            8: "1.1", 9: "1.2", 10: "2.1", 11: "2.2", 12: "3.1", 13: "3.2"
        }
        result = {}
        for group_key, cells in table.content.items():
            if group_key not in group_by_table_index:
                continue
            group = group_by_table_index[group_key]
            if group not in result:
                result[group] = []
            time_frames = result[group]
            for index, cell in enumerate(cells[1:]):  # Skip group name
                if is_orange(pixels, cell):
                    delta_start, delta_end = period_deltas(group_key, index)
                    start, end = day + delta_start, day + delta_end
                    if is_overlapping(time_frames, start):
                        last_period = time_frames[-1]
                        last_period[1] = end
                    else:
                        new_period = [start, end]
                        time_frames.append(new_period)
        return result, day
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return None, None


pattern = r'(\d{1,2}) (січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)\b'

month_map = {
    "січня": 1, "лютого": 2, "березня": 3, "квітня": 4, "травня": 5, "червня": 6,
    "липня": 7, "серпня": 8, "вересня": 9, "жовтня": 10, "листопада": 11, "грудня": 12
}


def parse_non_table(text):
    if not re.search("не застосовувати|не планують", text):
        return None, None
    date_match = re.findall(pattern, text)[0]
    day = int(date_match[0])
    month = month_map[date_match[1]]
    year = datetime.now().year
    date_obj = datetime(year, month, day)
    return {"1.1": [], "1.2": [], "2.1": [], "2.2": [], "3.1": [], "3.2": []}, date_obj


def is_overlapping(group_time_frames, start):
    return len(group_time_frames) > 0 and group_time_frames is not None and group_time_frames[-1][1] == start


def period_deltas(group_key, index):
    hours = index if group_key < 7 else index + 12
    return timedelta(hours=hours), timedelta(hours=hours + 1)


def extract_day(table):
    table_date = re.findall(r'\d{1,2}\.\d{1,2}\.\d{4}', table.title)[0]
    return datetime.strptime(table_date, "%d.%m.%Y")


def is_orange(pixels, cell):
    x, y = cell.bbox.x1 + 5, cell.bbox.y1 + 5  # move 5 pixels inwards into a cell
    color = pixels[x, y]
    return color[0] > 200 and color[1] > 100 and color[2] < 100
