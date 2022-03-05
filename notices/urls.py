from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('subscriber/<int:subscriber_id>/<str:subscriber_hash>/preview/<int:newsletter_id>/html', views.preview_html,
         name="preview_html"),
    path('subscriber/<int:subscriber_id>/<str:subscriber_hash>/preview/<int:newsletter_id>/text', views.preview_text,
         name="preview_text"),
    path('subscriber/<int:subscriber_id>/<str:subscriber_hash>/edit', views.subscriber_preferences,
         name="subscriber_preferences"),
    path('subscriber/<int:subscriber_id>/<str:subscriber_hash>/unsubscribe', views.subscriber_unsubscribe,
         name="subscriber_unsubscribe"),

    path('admin', views.admin_home, name='admin_home'),
    path('admin/tag/new', views.admin_new_tag, name='admin_new_tag'),
    path('admin/tag/<int:tag_id>/delete', views.admin_delete_tag, name='admin_delete_tag'),
    path('admin/tag/<int:tag_id>/edit', views.admin_edit_tag, name='admin_edit_tag'),
    path('admin/issue/new', views.admin_new_issue, name='admin_new_issue'),
    path('admin/issue/<int:newsletter_id>/preview', views.admin_preview_issue, name='admin_preview_issue'),
    path('admin/issue/<int:newsletter_id>/publish', views.admin_publish_issue, name='admin_publish_issue'),
    path('admin/issue/<int:newsletter_id>/edit', views.admin_edit_issue, name='admin_edit_issue'),

    path('admin/accounts/', include('django.contrib.auth.urls')),

]
