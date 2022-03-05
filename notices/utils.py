import datetime
from typing import List
import xml.etree.ElementTree as ET

from django.apps import apps
from django.conf import settings
import html2text
import requests
from django.template.loader import get_template, render_to_string

from notices.models import Notice, NoticeTag, Newsletter, Subscriber


def element_to_notice(elem: ET.Element):
    level = None
    subject = None
    body = None
    teacher = None

    meet_place = None
    meet_date = None
    meet_time = None
    meet_datetime = None

    for c in elem:
        t = c.tag
        x = c.text
        if t == "Level":
            level = x
        elif t == "Subject":
            subject = x
        elif t == "Body":
            body = x
        elif t == "Teacher":
            teacher = x
        elif t == "PlaceMeet":
            meet_place = x
        elif t == "DateMeet":
            meet_date = x
        elif t == "TimeMeet":
            meet_time = x

    if meet_date is not None and meet_time is not None:
        meet_datetime = f"{meet_date} {meet_time}"

    try:
        notice = Notice.objects.get(
            subject=subject,
            body=body,
            teacher=teacher,
            meeting_location=meet_place,
            datetime_text=meet_datetime
        )
    except Notice.DoesNotExist:
        notice = Notice(
            subject=subject,
            body=body,
            teacher=teacher,
            meeting_location=meet_place,
            datetime_text=meet_datetime,
        )

        notice.save()

        notice.tags.add(
            *NoticeTag.get_for_level(level)
        )

        notice.save()

    return notice


def kamar_api_query(command: str, **kwargs) -> ET:
    headers = {
        "User-Agent": "KAMAR/ Linux/ Android/",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(
        settings.KAMAR_API,
        headers=headers,
        data={
            "Key": "vtku",
            "Command": command,
            **kwargs
        },
    )

    return ET.fromstring(response.content)

def get_notices_by_date(date: datetime.date) -> List[Notice]:
    day_str = f"{date.day}/{date.month}/{date.year}"

    notice_xml = kamar_api_query(
        "GetNotices",
        Date = day_str
    )

    notices = [
                  element_to_notice(elem)
                  for elem in notice_xml.iter("Meeting")
              ] + [
                  element_to_notice(elem)
                  for elem in notice_xml.iter("General")
              ]

    return notices


def create_issue_for_date(issue_date: datetime.date):
    notices = get_notices_by_date(issue_date)

    issue = Newsletter(
        issue_date=issue_date
    )

    issue.save()

    issue.notices.add(*notices)
    issue.save()


def render_email_html(base_url, template_path, newsletter: Newsletter, subscriber: Subscriber):
    cfg = apps.get_app_config("notices")
    return render_to_string(template_path, {
        "newsletter": newsletter,
        "subscriber": subscriber,
        "school_name": cfg.school_name,
        "base_url": base_url
    })


def render_email_text(base_url, template_path, newsletter: Newsletter, subscriber: Subscriber):
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_emphasis = True
    h.ignore_tables = True

    return h.handle(render_email_html(base_url, template_path, newsletter, subscriber))
