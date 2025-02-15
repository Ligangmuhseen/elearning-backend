# Generated by Django 5.1.1 on 2024-09-14 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearning', '0003_chapter_enrollment_videos'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='videos',
            options={'verbose_name': 'Video', 'verbose_name_plural': 'Videos'},
        ),
        migrations.AlterField(
            model_name='videos',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
