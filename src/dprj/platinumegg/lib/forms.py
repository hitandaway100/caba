from django import forms as django_forms

class UploadFileForm(django_forms.Form):
    data_file  = django_forms.FileField()
