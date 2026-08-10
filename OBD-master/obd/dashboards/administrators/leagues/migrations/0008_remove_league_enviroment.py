from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0007_nationalrankingentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='league',
            name='enviroment',
        ),
    ]