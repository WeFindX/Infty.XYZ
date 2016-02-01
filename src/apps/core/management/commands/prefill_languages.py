# coding: utf-8
import MySQLdb

from django.core.management.base import BaseCommand
from core.models import Language


class Command(BaseCommand):
    help = 'prefill languages objects'

    def handle(self, *args, **options):
        self.prefill()

    def prefill(self):
        db = MySQLdb.connect(host="localhost", user="root", passwd="pwd",
                             db="omegawiki", charset='utf8')
        cur = db.cursor()
        # Language.objects.all().delete()
        cur.execute("select language_id, language_name from language_names where name_language_id = language_id;")
        for row in cur.fetchall():
            if row[1]:
                Language.objects.create(
                    pk=int(row[0]),
                    omegawiki_language_id=int(row[0]),
                    name=row[1]
                )
        cur.execute("select language_id, language_name from language_names where name_language_id = 85;")
        for row in cur.fetchall():
            try:
                Language.objects.get(omegawiki_language_id=int(row[0]))
            except Language.DoesNotExist:
                Language.objects.create(
                    pk=int(row[0]),
                    omegawiki_language_id=int(row[0]),
                    name=row[1]
                )
