from __future__ import annotations

import json
from pathlib import Path


def dict_list_to_json(dict_list: list[dict], filename: Path) -> str | None:
    try:
        json_str = json.dumps(dict_list, indent=4, ensure_ascii=False)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(json_str)
        return json_str
    except (TypeError, ValueError, IOError) as e:
        print(f"Ошибка при преобразовании списка словарей в JSON или записи в файл: {e}")
        return None


def json_to_dict_list(filename: Path) -> list[dict] | None:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            json_str = file.read()
        return json.loads(json_str)
    except (TypeError, ValueError, IOError) as e:
        print(f"Ошибка при преобразовании JSON в список словарей или чтении из файла: {e}")
        return None
