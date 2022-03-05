from django.contrib import admin

from .models import NoticeTag, Notice, Subscriber, Newsletter

# Register your models here.

admin.site.register(Notice)
admin.site.register(NoticeTag)
admin.site.register(Subscriber)
admin.site.register(Newsletter)