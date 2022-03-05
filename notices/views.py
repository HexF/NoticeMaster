from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_datetime
from django.views.decorators.clickjacking import xframe_options_exempt

from notices.forms import TagForm, CreateIssueForm, SubscribeForm
from notices.models import Subscriber, NoticeTag, Newsletter, Notice
from notices.utils import create_issue_for_date, render_email_html, render_email_text


def index(request):
    if request.method == "POST":
        form = SubscribeForm(request.POST)

        if form.is_valid():
            form.save()

            return render(request, 'noticemaster/subscribed.html', {
                "subscriber": form.instance,
                "school_name": apps.get_app_config("notices").school_name
            })

    else:
        form = SubscribeForm()

    return render(request, 'noticemaster/subscribe.html', {
        "form": form,
        "school_name": apps.get_app_config("notices").school_name
    })


def subscriber_preferences(request, subscriber_id, subscriber_hash):
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    assert subscriber.hash() == subscriber_hash

    if request.method == "POST":
        subscriber.unsubscribed_tags.clear()
        for tag in request.POST.getlist("optout"):
            subscriber.unsubscribed_tags.add(int(tag))

        subscriber.save()

    return render(request, "noticemaster/edit_subscription.html", {
        "subscriber": subscriber,
        "tags": NoticeTag.objects.order_by("type", "name").all(),
        "school_name": apps.get_app_config("notices").school_name,
        "tag_categories": NoticeTag.TagType.choices,
    })


def subscriber_unsubscribe(request, subscriber_id, subscriber_hash):
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    assert subscriber.hash() == subscriber_hash
    subscriber.delete()
    return render(request, "noticemaster/unsubscribed.html", {
        "school_name": apps.get_app_config("notices").school_name,
        "subscriber": subscriber
    })


# Admin

@login_required
def admin_home(request):
    return render(request, "noticemaster/admin/index.html", {
        "issues": Newsletter.objects.all(),
        "tags": NoticeTag.objects.all,
        "subscribers": Subscriber.objects.all(),

        "create_tag_form": TagForm(),
        "create_issue_form": CreateIssueForm()
    })


# Tag CRUD
@login_required
def admin_new_tag(request):
    form = TagForm(request.POST)

    if form.is_valid():
        form.save()

    return redirect("admin_home")

@login_required
def admin_delete_tag(request, tag_id):
    tag = get_object_or_404(NoticeTag, id=tag_id)
    if Notice.objects.filter(tags__in=[tag]).count() == 0:
        tag.delete()
    return redirect("admin_home")

@login_required
def admin_edit_tag(request, tag_id):
    tag = get_object_or_404(NoticeTag, id=tag_id)
    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)

        if form.is_valid():
            form.save()
            return redirect("admin_home")
    else:
        form = TagForm(instance=tag)

    return render(request, "noticemaster/admin/edit_tag.html", {
        "form": form
    })


# Issues
@login_required
def admin_new_issue(request):
    form = CreateIssueForm(request.POST)
    if form.is_valid():
        create_issue_for_date(form.cleaned_data["issue_date"])

    return redirect("admin_home")

@login_required
def admin_edit_issue(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)

    if request.method == "POST":
        for notice in newsletter.notices.all():
            prefix = f"notice[{notice.id}]."
            time = request.POST[prefix + "time"]
            if len(time) > 0:
                newsletter.set_override(notice, "meeting_time", time)
                newsletter.set_override(notice, "event_time", time)

                notice.meeting_time = parse_datetime(time)
                notice.event_time = parse_datetime(time)
            else:
                notice.meeting_time = None
                notice.event_time = None

            notice.tags.clear()

            for tag in request.POST.getlist(prefix + "tags"):
                try:
                    notice.tags.add(int(tag))
                except ValueError:
                    # creating a tag
                    new_tag = NoticeTag(name=tag, type=NoticeTag.TagType.UNSPECIFIED)
                    new_tag.save()
                    notice.tags.add(new_tag)

            notice.save()

        return redirect("admin_home")

    cfg = apps.get_app_config("notices")

    return render(request, "noticemaster/admin/edit_issue.html", {
        "newsletter": newsletter,
        "tags": NoticeTag.objects.all(),
        "period_times": cfg.period_times,
        "period_names": cfg.period_names
    })

@login_required
def admin_publish_issue(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    base_url = "http://" + request.META["HTTP_HOST"]
    newsletter.publish(base_url)
    return redirect("admin_home")
@login_required
def admin_preview_issue(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
    try:
        dummy_subscriber = Subscriber.objects.get(
            email="dummy-subscriber@example.com",
            is_subscribed=False
        )
    except Subscriber.DoesNotExist:
        dummy_subscriber = Subscriber(
            email="dummy-subscriber@example.com",
            is_subscribed=False
        )
        dummy_subscriber.save()

    return render(request, "noticemaster/admin/preview_issue.html", {
        "newsletter": newsletter,
        "dummy_subscriber": dummy_subscriber
    })


@xframe_options_exempt
def preview_html(request, subscriber_id, subscriber_hash, newsletter_id):
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    assert subscriber.hash() == subscriber_hash

    base_url = "http://" + request.META["HTTP_HOST"]

    return HttpResponse(
        render_email_html(base_url, "noticemaster/email/newsletter.mjml",
                          get_object_or_404(Newsletter, id=newsletter_id),
                          subscriber
                          )
    )


@xframe_options_exempt
def preview_text(request, subscriber_id, subscriber_hash, newsletter_id):
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    assert subscriber.hash() == subscriber_hash
    base_url = "http://" + request.META["HTTP_HOST"]

    return HttpResponse(
        render_email_text(base_url, "noticemaster/email/newsletter.mjml",
                          get_object_or_404(Newsletter, id=newsletter_id),
                          subscriber
                          ),
        content_type="text/plain"
    )

