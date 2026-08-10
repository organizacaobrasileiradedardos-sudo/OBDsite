from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enviroments', '0007_alter_enviroment_id'),
        ('leagues', '0008_remove_league_enviroment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Enviroment',
        ),
    ]