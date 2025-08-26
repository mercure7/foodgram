import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):
    help = 'Наполняет данными таблицу Ингредиенты '
    model = Ingredients

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        with open(csv_file_path, 'r', encoding="UTF-8") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                self.model.objects.create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
            print(f'Импорт из {csv_file_path} произведен.')
