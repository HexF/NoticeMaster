# Generated by Django 4.0.3 on 2022-03-04 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notices', '0004_remove_subscriber_is_admin_notice_event_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='datetime_text',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
