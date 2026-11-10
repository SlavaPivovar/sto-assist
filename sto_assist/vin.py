"""Декодер VIN: марка за кодом виробника (WMI), модельний рік, контрольна цифра.

Марку визначаємо для поширених виробників; модель із VIN у загальному випадку не визначається
(кожен виробник кодує її по-своєму) — її вказує майстер. Для Tesla модель і завод розшифровуються.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

TESLA_WMI = {
    "5YJ": "Tesla, Inc. (США, легкові)",
    "7SA": "Tesla, Inc. (США, MPV/SUV)",
    "7G2": "Tesla, Inc. (США, Cybertruck/Semi)",
    "LRW": "Tesla (Китай, Шанхай)",
    "XP7": "Tesla (Німеччина, Берлін)",
    "SFZ": "Tesla Roadster (Велика Британія)",
}

# Марка за WMI: спершу шукаємо всі три символи, потім перші два.
MAKES = {
    **{w: "Tesla" for w in TESLA_WMI},
    # Німеччина
    "WVW": "Volkswagen", "WV1": "Volkswagen", "WV2": "Volkswagen", "WVG": "Volkswagen", "3VW": "Volkswagen",
    "1VW": "Volkswagen", "9BW": "Volkswagen", "LSV": "Volkswagen", "LFV": "Volkswagen",
    "WAU": "Audi", "WA1": "Audi", "TRU": "Audi",
    "WBA": "BMW", "WBS": "BMW", "WBX": "BMW", "WBY": "BMW", "5UX": "BMW", "5YM": "BMW", "4US": "BMW",
    "WMW": "MINI", "WME": "smart",
    "WDB": "Mercedes-Benz", "WDC": "Mercedes-Benz", "WDD": "Mercedes-Benz", "WDF": "Mercedes-Benz",
    "W1K": "Mercedes-Benz", "W1N": "Mercedes-Benz", "W1V": "Mercedes-Benz", "4JG": "Mercedes-Benz",
    "55S": "Mercedes-Benz",
    "WP0": "Porsche", "WP1": "Porsche", "W0L": "Opel", "W0V": "Opel", "VXK": "Opel",
    "WF0": "Ford",
    # Чехія, Іспанія, Франція, Румунія, Італія, Швеція, Британія
    "TMB": "Škoda", "VSS": "SEAT", "VF1": "Renault", "VF6": "Renault", "UU1": "Dacia",
    "VF3": "Peugeot", "VR3": "Peugeot", "VF7": "Citroën", "VR7": "Citroën", "VR1": "DS",
    "ZFA": "Fiat", "ZAR": "Alfa Romeo", "ZLA": "Lancia", "ZAM": "Maserati", "ZFF": "Ferrari", "ZHW": "Lamborghini",
    "YV1": "Volvo", "YV4": "Volvo", "LVY": "Volvo", "7JR": "Volvo", "YS3": "Saab",
    "SAL": "Land Rover", "SAJ": "Jaguar",
    # США
    "1FA": "Ford", "1FM": "Ford", "1FT": "Ford", "1FD": "Ford", "3FA": "Ford", "NM0": "Ford",
    "5LM": "Lincoln", "1LN": "Lincoln",
    "1G1": "Chevrolet", "1GC": "Chevrolet", "1GN": "Chevrolet", "2G1": "Chevrolet", "3G1": "Chevrolet",
    "KL1": "Chevrolet", "1G6": "Cadillac", "1GY": "Cadillac", "1G4": "Buick", "1GT": "GMC", "1GK": "GMC",
    "1C3": "Chrysler", "2C3": "Chrysler", "2C4": "Chrysler", "1B3": "Dodge", "2B3": "Dodge",
    "1J4": "Jeep", "1J8": "Jeep", "1C4": "Jeep", "1C6": "Ram", "3C6": "Ram",
    # Японія
    "JT": "Toyota", "4T1": "Toyota", "5TD": "Toyota", "2T1": "Toyota", "5YF": "Toyota", "VNK": "Toyota",
    "SB1": "Toyota", "NMT": "Toyota", "JTH": "Lexus", "JTJ": "Lexus", "2T2": "Lexus",
    "JHM": "Honda", "JHL": "Honda", "1HG": "Honda", "2HG": "Honda", "5J6": "Honda", "SHH": "Honda", "19X": "Honda",
    "JH4": "Acura", "19U": "Acura", "5J8": "Acura",
    "JN1": "Nissan", "JN8": "Nissan", "1N4": "Nissan", "3N1": "Nissan", "5N1": "Nissan", "SJN": "Nissan",
    "VSK": "Nissan", "JNK": "Infiniti",
    "JM1": "Mazda", "JM3": "Mazda", "JMZ": "Mazda", "3MZ": "Mazda",
    "JA3": "Mitsubishi", "JA4": "Mitsubishi", "JMB": "Mitsubishi", "JMY": "Mitsubishi", "4A3": "Mitsubishi",
    "JF1": "Subaru", "JF2": "Subaru", "4S3": "Subaru", "4S4": "Subaru", "JS": "Suzuki", "TSM": "Suzuki",
    # Корея
    "KMH": "Hyundai", "KM8": "Hyundai", "5NP": "Hyundai", "5NM": "Hyundai", "TMA": "Hyundai", "NLH": "Hyundai",
    "KNA": "Kia", "KND": "Kia", "KNE": "Kia", "5XY": "Kia", "5XX": "Kia", "U5Y": "Kia",
    "KMT": "Genesis", "KPT": "SsangYong", "KLA": "Daewoo",
    # Китай
    "LGX": "BYD", "LC0": "BYD", "L6T": "Geely", "LB3": "Geely", "LVV": "Chery", "LVT": "Chery",
    "LGW": "Haval / Great Wall", "LSJ": "MG", "LJ1": "NIO",
    # Україна та сусіди
    "Y6D": "ZAZ", "XTA": "Lada", "XTT": "UAZ",
}

MODELS = {
    "S": ("MODEL_S", "Model S"),
    "3": ("MODEL_3", "Model 3"),
    "X": ("MODEL_X", "Model X"),
    "Y": ("MODEL_Y", "Model Y"),
    "C": ("CYBERTRUCK", "Cybertruck"),
    "R": ("ROADSTER", "Roadster"),
    "T": ("SEMI", "Semi"),
}

PLANTS = {
    "F": "Фрімонт, Каліфорнія (США)",
    "A": "Остін, Техас (США)",
    "P": "Пало-Альто, Каліфорнія (США)",
    "N": "Ріно, Невада (США)",
    "C": "Шанхай (Китай)",
    "B": "Берлін (Німеччина)",
}

# Код модельного року (10-та позиція) повторюється кожні 30 років: A = 1980, 2010, 2040…
_YEAR_CODES = "ABCDEFGHJKLMNPRSTVWXY123456789"


def model_year(code: str, today: date | None = None) -> int | None:
    """Найновіший рік із циклу, що не пізніший за наступний календарний (авто «наступного модельного року»)."""
    if code not in _YEAR_CODES:
        return None
    limit = (today or date.today()).year + 1
    year = 1980 + _YEAR_CODES.index(code)
    while year + 30 <= limit:
        year += 30
    return year

_TRANSLIT = {
    **{str(d): d for d in range(10)},
    **dict(zip("ABCDEFGH", range(1, 9))),
    **dict(zip("JKLMN", range(1, 6))),
    "P": 7, "R": 9,
    **dict(zip("STUVWXYZ", range(2, 10))),
}
_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]


@dataclass
class VinInfo:
    vin: str
    valid: bool
    make: str | None = None  # марка: Tesla, Volkswagen, Toyota…
    manufacturer: str | None = None
    model_code: str | None = None
    model_name: str | None = None
    year: int | None = None
    plant: str | None = None
    serial: str | None = None
    warnings: list[str] = field(default_factory=list)


def check_digit(vin: str) -> str:
    total = sum(_TRANSLIT[ch] * w for ch, w in zip(vin, _WEIGHTS))
    rem = total % 11
    return "X" if rem == 10 else str(rem)


def decode_vin(raw: str) -> VinInfo:
    vin = raw.strip().upper().replace(" ", "")
    info = VinInfo(vin=vin, valid=False)
    if len(vin) != 17:
        info.warnings.append(f"VIN має містити 17 символів, отримано {len(vin)}")
        return info
    bad = sorted({ch for ch in vin if ch not in _TRANSLIT})
    if bad:
        info.warnings.append(f"Неприпустимі символи у VIN: {', '.join(bad)} (літери I, O, Q не використовуються)")
        return info

    info.serial = vin[11:]
    info.make = MAKES.get(vin[:3]) or MAKES.get(vin[:2])
    north_america = vin[0] in "123457"
    if info.make == "Tesla":
        info.manufacturer = TESLA_WMI[vin[:3]]
        model = MODELS.get(vin[3])
        if model:
            info.model_code, info.model_name = model
        else:
            info.warnings.append(f"Невідомий код моделі «{vin[3]}» (4-та позиція)")
        info.plant = PLANTS.get(vin[10])
        if info.plant is None:
            info.warnings.append(f"Невідомий код заводу «{vin[10]}»")
    elif info.make is None:
        info.warnings.append(f"Марку за VIN не визначено (код виробника «{vin[:3]}») — вкажіть марку й модель вручну")

    # Рік у 10-й позиції гарантовано кодують Північна Америка, Tesla й більшість азійських виробників;
    # європейські заводи часто ставлять там довільний символ, тож для них рік не підставляємо.
    european = vin[0] in "STUVWXYZ" and info.make != "Tesla"
    if not european:
        info.year = model_year(vin[9])
        if info.year is None:
            info.warnings.append(f"Невідомий код модельного року «{vin[9]}»")

    # Контрольна цифра обов'язкова для ринку Північної Америки.
    if north_america and check_digit(vin) != vin[8]:
        info.warnings.append(
            f"Контрольна цифра не збігається (очікувалась «{check_digit(vin)}», у VIN «{vin[8]}») — перевірте VIN"
        )

    info.valid = True
    return info
