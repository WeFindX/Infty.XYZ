# coding: utf-8
import MySQLdb

from django.core.management.base import BaseCommand
from core.models import Language, Definition
from users.models import User

class Command(BaseCommand):
    help = 'prefill definitions objects'

    def handle(self, *args, **options):
        self.prefill()

    def prefill(self):
        db = MySQLdb.connect(host="localhost", user="root", passwd="pwd",
                             db="omegawiki", charset='utf8')
        cur = db.cursor()

        #for definition in Definition.objects.all():
        #    definition.delete()

        query = lambda lang_id: '''select uw_expression.spelling, uw_text.text_text,uw_syntrans.defined_meaning_id 
             from uw_text, uw_translated_content, uw_defined_meaning, uw_syntrans, uw_expression 
             where uw_translated_content.language_id = %s
             and uw_expression.language_id = %s
             and uw_defined_meaning.meaning_text_tcid = uw_translated_content.translated_content_id 
             and uw_text.text_id = uw_translated_content.text_id 
             and uw_defined_meaning.defined_meaning_id = uw_syntrans.defined_meaning_id 
             and uw_expression.expression_id = uw_syntrans.expression_id 
             and uw_translated_content.remove_transaction_id is NULL 
             and uw_syntrans.remove_transaction_id is NULL;''' % (lang_id,lang_id)

        user = User.objects.get(id=1)
        for language in Language.objects.all():
            cur.execute(query(language.omegawiki_language_id))
            for row in cur.fetchall():
                if row[1]:
                    try:
                        Definition.objects.create(name=row[0],
                                            definition=row[1],
                                            defined_meaning_id=row[2],
                                            language=language,
                                            user=user)
                    except Exception:
                        ''' Duplicate? '''
                        pass
