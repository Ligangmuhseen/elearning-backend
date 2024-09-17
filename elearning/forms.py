# yourapp/forms.py
from django import forms
from .models import Videos
from django.core.exceptions import ValidationError

# class VideoUploadForm(forms.ModelForm):
#     video_file = forms.FileField(required=True)

#     class Meta:
#         model = Videos
#         fields = ['title', 'description', 'video_url','chapter','video_file']


class VideoAdminForm(forms.ModelForm):
    video_file = forms.FileField(required=True)

    class Meta:
        model = Videos
        fields =  ['title', 'description', 'video_url','chapter','video_file']

    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            if video_file.size > 100 * 1024 * 1024:  # 100 MB limit
                raise ValidationError("File size must be under 100 MB.")
            if not video_file.name.lower().endswith(('.mp4', '.mov', '.avi')):
                raise ValidationError("Only .mp4, .mov, and .avi files are allowed.")
        return video_file