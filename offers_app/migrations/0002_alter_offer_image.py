from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='offer_images/'),
        ),
    ]
