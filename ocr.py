import logging
import re
from datetime import datetime, timedelta
from img2table.document import Image
from img2table.ocr import TesseractOCR
from PIL import Image as PILImage


def image_to_time_frames(image_path):
    image = Image(image_path, detect_rotation=False)
    pixels = PILImage.open(image_path).load()

    logging.info("Extracting tables from image...")
    extracted_tables = image.extract_tables(
        ocr=TesseractOCR(n_threads=1, lang="ukr", psm=11),
        implicit_rows=False,
        implicit_columns=False,
        borderless_tables=False,
        min_confidence=1)
    logging.info(f"Extracted {len(extracted_tables)} tables from image.")
    
    if len(extracted_tables) == 0:
        logging.warn("No tables found in the image.")
        return None, None

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
