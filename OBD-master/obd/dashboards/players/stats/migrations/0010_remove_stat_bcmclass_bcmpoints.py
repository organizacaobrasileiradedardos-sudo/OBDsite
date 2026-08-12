from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0009_alter_stat_id'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='stat',
                    name='bcmClass',
                ),
                migrations.RemoveField(
                    model_name='stat',
                    name='bcmPoints',
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE stats_stat DROP COLUMN IF EXISTS "bcmClass";
                        ALTER TABLE stats_stat DROP COLUMN IF EXISTS "bcmPoints";
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]