from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leagues', '0005_alter_league_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderOfMeritEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_in_stage', models.IntegerField(blank=True, null=True, verbose_name='Posição na Etapa')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Valor (R$)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_of_merit_entries', to='leagues.league')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_of_merit_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'order of merit entry',
                'verbose_name_plural': 'order of merit entries',
                'ordering': ('-league__start_date',),
                'unique_together': {('player', 'league')},
            },
        ),
    ]