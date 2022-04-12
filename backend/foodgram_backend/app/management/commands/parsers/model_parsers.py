import csv
import os

from django.conf import settings
from django.shortcuts import get_object_or_404

from app.models import Ingredient, MeasurementUnit


def csv_parser(file):
    """Выносим общий для всех парсеров функционал по csv."""
    file_path = os.path.join(settings.BASE_DIR, file)
    result = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            result.append(row)
    return result


def ingredient_parser(file):
    """Парсер для модели ингредиентов."""
    rows = csv_parser(file)
    units = set([row[1] for row in rows])
    objs = [MeasurementUnit(name=unit) for unit in units]
    MeasurementUnit.objects.bulk_create(objs)
    for row in rows:
        measurement_unit = get_object_or_404(MeasurementUnit, name=row[1])
        obj, created = Ingredient.objects.get_or_create(name=row[0])
        print(row[0])
        obj.measurement_unit.add(measurement_unit)
        obj.save()
