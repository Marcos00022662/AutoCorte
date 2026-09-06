import secrets

from django.db import migrations


def preencher_tokens(apps, schema_editor):
    Agendamento = apps.get_model("core", "Agendamento")
    for agendamento in Agendamento.objects.filter(token__isnull=True):
        agendamento.token = secrets.token_urlsafe(16)
        agendamento.save(update_fields=["token"])


def reverter(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_agendamento_token'),
    ]

    operations = [
        migrations.RunPython(preencher_tokens, reverter),
    ]