from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0030_alter_profile_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_verified',
            field=models.BooleanField(default=True, verbose_name='Verificado'),
        ),
    ]