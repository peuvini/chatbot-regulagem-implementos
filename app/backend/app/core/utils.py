from __future__ import annotations

import math
import re
import unicodedata
from typing import Any


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text.lower())


def clean_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    if not text or text.upper() == "ND" or text.lower() == "nan":
        return None
    return text


def first_number(value: Any) -> float | None:
    text = clean_value(value)
    if not text:
        return None
    match = re.search(r"-?\d+(?:[.,]\d+)?", text)
    if not match:
        return None
    token = match.group(0)
    if "," in token:
        return float(token.replace(".", "").replace(",", "."))
    if "." in token:
        left, right = token.split(".", 1)
        if len(right) == 3 and len(left) <= 2:
            return float(left + right)
        return float(token)
    return float(token)


def parse_range(value: Any) -> tuple[float | None, float | None, float | None]:
    text = clean_value(value)
    if not text:
        return None, None, None
    numbers = [first_number(item) for item in re.findall(r"-?\d+(?:[.,]\d+)?", text)]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return None, None, None
    low = min(numbers)
    high = max(numbers)
    return low, high, (low + high) / 2


def numeric_or_none(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    return first_number(value)


def mean_present(values: list[Any]) -> float | None:
    numbers = [numeric_or_none(value) for value in values]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)

