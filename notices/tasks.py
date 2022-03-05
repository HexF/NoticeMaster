import datetime

from django.apps import apps
from django.core.mail import send_mail

from .utils import get_notices_by_date, render_email_text, render_email_html
from .models import Newsletter, Subscriber


def create_newsletter():
    """
    Gathers all the notices for today's newsletter, and creates the newsletter, notifying admins to tag posts.
    Should be run at ~9AM every day.
    """

    issue_date = datetime.date.today()

    notices = get_notices_by_date(issue_date)

    issue = Newsletter(
        issue_date=issue_date
    )

    issue.save()

    issue.notices.add(*notices)
    issue.save()


def render_and_email_newsletter(base_url, newsletter_id, subscriber_id):
    newsletter = Newsletter.objects.get(id=newsletter_id)
    subscriber = Subscriber.objects.get(id=subscriber_id)

    rendered_plain = render_email_text(base_url, "noticemaster/email/newsletter.mjml", newsletter, subscriber)
    rendered_html = render_email_html(base_url, "noticemaster/email/newsletter.mjml", newsletter, subscriber)

    school_name = apps.get_app_config('notices').school_name

    send_mail(
        f"{school_name} Notices for {newsletter.issue_date}",
        rendered_plain,
        "notices@hexdev.nz",
        [subscriber.email],
        html_message=rendered_html
    )

    subscriber.last_sent = newsletter.issue_date
    subscriber.save()
