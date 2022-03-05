import hashlib
import json

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_q.tasks import schedule


class NoticeTag(models.Model):
    class TagType(models.TextChoices):
        GENERAL = 'G', _("General")
        ARTS = "A", _("Arts")
        SPORTS = 'S', _("Sports")
        EVENTS = 'E', _("Events")
        YEAR_LEVEL = 'Y', _("Year Level")
        CLUBS = 'C', _("Clubs")
        UNSPECIFIED = 'U', _("Unspecified")
        SCHOLARSHIP = 'H', _("Scholarship")

    type = models.CharField(
        max_length=1,
        choices=TagType.choices,
        default=TagType.UNSPECIFIED
    )

    name = models.CharField(
        max_length=50
    )

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

    def notices(self):
        return Notice.objects.filter(tags__in=[self])

    @classmethod
    def get_for_level(cls, level):
        try:
            tag = cls.objects.get(
                type=NoticeTag.TagType.YEAR_LEVEL,
                name=level
            )
        except NoticeTag.DoesNotExist:
            tag = NoticeTag(
                type=NoticeTag.TagType.YEAR_LEVEL,
                name=level
            )

            tag.save()

        return [tag]


class Notice(models.Model):
    tags = models.ManyToManyField(NoticeTag)

    subject = models.CharField(
        max_length=1000
    )
    body = models.CharField(
        max_length=10000
    )
    teacher = models.CharField(
        max_length=50
    )

    datetime_text = models.CharField(
        max_length=100,
        null=True
    )

    # Meeting fields are null if its not a meeting
    meeting_location = models.CharField(null=True, max_length=50)
    meeting_time = models.DateTimeField(null=True)

    # Event fields are null if not an event
    event_time = models.DateField(null=True)

    def is_meeting(self):
        return self.meeting_time is not None and self.meeting_time is not None

    def __str__(self):
        if self.is_meeting():
            return f"{self.subject} Meeting"

        return f"{self.subject}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    last_sent = models.DateTimeField(null=True)
    is_subscribed = models.BooleanField(default=True)
    unsubscribed_tags = models.ManyToManyField(NoticeTag)

    def hash(self):
        m = hashlib.sha256()
        m.update(b"Subscriber Email")
        m.update(settings.SECRET_KEY.encode())
        m.update(str(self.email).encode())
        return m.digest().hex()


class Newsletter(models.Model):
    published = models.BooleanField(default=False)
    issue_date = models.DateField()
    overrides_json = models.CharField(null=False, default="{}", max_length=500000)
    notices = models.ManyToManyField(Notice)

    def set_override(self, notice: Notice, field: str, value: str):
        overrides = json.loads(self.overrides_json)
        nid = notice.pk
        if nid not in overrides:
            overrides[nid] = {}

        overrides[nid][field] = value

        self.overrides_json = json.dumps(overrides)

    def get_overrides(self, notice: Notice):
        overrides = json.loads(self.overrides_json)

        if notice.pk in overrides:
            return overrides[notice.pk]
        return {}

    def publish(self, base_url):
        if not self.published:
            self.published = True
            self.save()

            for subscriber in Subscriber.objects.all():
                if subscriber.is_subscribed:
                    schedule(
                        'notices.tasks.render_and_email_newsletter',
                        base_url, self.id, subscriber.id,
                        schedule_type="O",  # Once

                    )

    # Notice categories

    def meetings(self):
        return self.notices.filter(
            meeting_location__isnull=False,
            meeting_time__isnull=False
        )

    def events(self):
        return self.notices.filter(
            tags__type=NoticeTag.TagType.EVENTS
        )

    def sports(self):
        return self.notices.filter(
            tags__type=NoticeTag.TagType.SPORTS
        )

    def general_notices(self):
        return self.notices.filter(
            meeting_location__isnull=True,
            meeting_time__isnull=True,
            event_time__isnull=True
        ).exclude(
            tags__type__in=[
                NoticeTag.TagType.SPORTS,
                NoticeTag.TagType.EVENTS
            ]
        )

    def remaining_notices(self):
        return self.notices.exclude(
            self.general_notices(),
            self.sports(),
            self.events(),
            self.meetings()
        )

    def __str__(self):
        return f"Newsletter for {self.issue_date}"
