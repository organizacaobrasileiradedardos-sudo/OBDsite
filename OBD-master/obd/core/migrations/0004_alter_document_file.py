import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_playertournamentstat_player'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='file',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='Arquivo'),
        ),
    ]