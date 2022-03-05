from django import forms

from notices.models import NoticeTag, Subscriber


class CreateIssueForm(forms.Form):
    issue_date = forms.DateField(label="Date", widget=forms.TextInput(
        attrs={'type': 'date'}
    ))


class TagForm(forms.ModelForm):
    class Meta:
        model = NoticeTag
        fields = ['type', 'name']


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']