from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_preencher_tokens'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agendamento',
            name='token',
            field=models.CharField(blank=True, editable=False, max_length=32, unique=True),
        ),
    ]