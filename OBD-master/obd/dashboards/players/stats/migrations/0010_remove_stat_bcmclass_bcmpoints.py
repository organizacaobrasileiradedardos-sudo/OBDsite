from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0009_alter_stat_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stat',
            name='bcmClass',
        ),
        migrations.RemoveField(
            model_name='stat',
            name='bcmPoints',
        ),
    ]