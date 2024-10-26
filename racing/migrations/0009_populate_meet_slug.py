from django.db import migrations
from django.utils.text import slugify

def populate_slug(apps, schema_editor):
    Meet = apps.get_model('racing', 'Meet')
    for meet in Meet.objects.all():
        meet.slug = slugify(meet.name)
        meet.save()

class Migration(migrations.Migration):

    dependencies = [
        ('racing', '0008_meet_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slug),
    ]