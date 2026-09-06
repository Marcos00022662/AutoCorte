from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_servico_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendamento',
            name='token',
            field=models.CharField(blank=True, editable=False, max_length=32, null=True),
        ),
    ]