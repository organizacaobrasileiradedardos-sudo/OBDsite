from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0029_alter_profile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='pin',
            field=models.CharField(max_length=50, null=False, blank=True),
        ),
    ]
