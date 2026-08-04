from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('champions', '0004_alter_champion_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='champion',
            name='p1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='p1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='champion',
            name='p2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='p2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='champion',
            name='p3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='p3', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='champion',
            name='p4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='p4', to=settings.AUTH_USER_MODEL),
        ),
    ]