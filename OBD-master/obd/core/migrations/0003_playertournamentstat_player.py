from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_tournamentresult_playertournamentstat'),
    ]

    operations = [
        migrations.AddField(
            model_name='playertournamentstat',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_stats', to=settings.AUTH_USER_MODEL),
        ),
    ]