# Generated by Django 4.0.3 on 2022-03-04 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notices', '0006_alter_notice_event_time_alter_noticetag_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscriber',
            old_name='subscribed_tags',
            new_name='unsubscribed_tags',
        ),
        migrations.AlterField(
            model_name='noticetag',
            name='type',
            field=models.CharField(choices=[('G', 'General'), ('A', 'Arts'), ('S', 'Sports'), ('E', 'Events'), ('Y', 'Year Level'), ('C', 'Clubs'), ('U', 'Unspecified'), ('H', 'Scholarship')], default='U', max_length=1),
        ),
    ]
