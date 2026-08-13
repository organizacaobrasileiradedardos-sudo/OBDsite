import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_document_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='flyer',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='Flyer'),
        ),
    ]