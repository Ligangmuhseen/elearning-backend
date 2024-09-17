from django.contrib import admin
import tempfile
from django.utils.html import format_html
from django.urls import reverse
from .models import Course,Chapter,Videos,Enrollment,VideoProgress
from .forms import VideoAdminForm
from django.core.exceptions import ValidationError
from django.shortcuts import render,redirect
import vimeo
from django.conf import settings
import requests



class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'date_posted', 'custom_actions')
    list_filter = ('date_posted','title')
    search_fields = ('title',)
    ordering = ('-date_posted',)
    

    def custom_actions(self, obj):
        view_url = reverse('admin:elearning_course_change', args=[obj.pk])
        delete_url = reverse('admin:elearning_course_delete', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}">Edit</a> | '
            '<a class="button" href="{}" style="color:red;" onclick="return confirm(\'Are you sure you want to delete?\')">Delete</a>',
            view_url, delete_url
        )
    
    custom_actions.short_description = 'Actions'

    

admin.site.register(Course, CourseAdmin)



class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'course', 'custom_actions')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('-title',)
    

    def custom_actions(self, obj):
        view_url = reverse('admin:elearning_chapter_change', args=[obj.pk])
        delete_url = reverse('admin:elearning_chapter_delete', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}">Edit</a> | '
            '<a class="button" href="{}" style="color:red;" onclick="return confirm(\'Are you sure you want to delete?\')">Delete</a>',
            view_url, delete_url
        )
    
    custom_actions.short_description = 'Actions'


admin.site.register(Chapter, ChapterAdmin)



import json


@admin.register(Videos)
class VideosAdmin(admin.ModelAdmin):
    

    list_display = ('title', 'description','chapter', 'video_url', 'custom_actions')
    list_filter = ('chapter', 'uploaded_at')
    search_fields = ('title', 'chapter__title')
    ordering = ('-uploaded_at',)
    readonly_fields=('video_url',)

    def custom_actions(self, obj):
        view_url = reverse('admin:elearning_videos_change', args=[obj.pk])
        delete_url = reverse('admin:elearning_videos_delete', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}">Edit</a> | '
            '<a class="button" href="{}" style="color:red;" onclick="return confirm(\'Are you sure you want to delete?\')">Delete</a>',
            view_url, delete_url
        )
    
    custom_actions.short_description = 'Actions'

    

    form = VideoAdminForm

    def save_model(self, request, obj, form, change):
        video_file = form.cleaned_data.get('video_file')
        if video_file:
            headers = {
                'Authorization': f'bearer {settings.VIMEO_ACCESS_TOKEN}',
                'Content-Type': 'application/json',
                'Accept': 'application/vnd.vimeo.*+json;version=3.4'
            }
            try:
                # Check if the video URL exists (indicating an update)
                if obj.video_url:
                    # Extract the Vimeo video ID from the URL
                    video_id = obj.video_url.split('/')[-1]
                    vimeo_url = f"https://api.vimeo.com/videos/{video_id}"

                    # Step 0: Delete the existing video (to allow file replacement)
                    delete_response = requests.delete(vimeo_url, headers=headers, timeout=60)
                    
                    if delete_response.status_code != 204:  # 204 is the expected status for successful deletion
                        raise ValidationError(f"Failed to delete existing video: {delete_response.json().get('error', delete_response.text)}")
                    
                # Step 1: Create the video on Vimeo
                url = 'https://api.vimeo.com/me/videos'
                video_data = {
                    'upload': {
                        'approach': 'tus',
                        'size': video_file.size
                    },
                    'name': obj.title,
                    'description': obj.description
                }
               
                response = requests.post(url, headers=headers, data=json.dumps(video_data), timeout=60)
                
                if response.status_code != 200:
                    raise ValidationError(f"Failed to create video: {response.json().get('error', response.text)}")
                
                upload_link = response.json().get('upload', {}).get('upload_link')
                if not upload_link:
                    raise ValidationError("Failed to get upload link from Vimeo")
                
                # Step 2: Upload the video file using PATCH
                video_file.seek(0)  # Ensure the file pointer is at the beginning
                file_size = video_file.size
                upload_offset = 0
                
                while upload_offset < file_size:
                    video_file.seek(upload_offset)
                    chunk_size = min(file_size - upload_offset, 512 * 1024 * 1024)  # 512 MB chunk size
                    chunk_data = video_file.read(chunk_size)
                    
                    headers = {
                        'Tus-Resumable': '1.0.0',
                        'Upload-Offset': str(upload_offset),
                        'Content-Type': 'application/offset+octet-stream'
                    }
                    upload_response = requests.patch(upload_link, data=chunk_data, headers=headers)
                    
                    if upload_response.status_code not in [200, 204]:
                        raise ValidationError(f"Failed to upload video chunk: {upload_response.json().get('error', upload_response.text)}")
                    
                    upload_offset = int(upload_response.headers.get('Upload-Offset', upload_offset))
                    
                    # Verify upload status
                    status_response = requests.head(upload_link, headers={
                        'Tus-Resumable': '1.0.0',
                        'Accept': 'application/vnd.vimeo.*+json;version=3.4'
                    })
                    
                    if status_response.status_code != 200:
                        raise ValidationError("Failed to verify upload status")
                    
                    upload_length = int(status_response.headers.get('Upload-Length', 0))
                    if upload_length == upload_offset:
                        break  # Upload completed
                
                # Step 3: Verify the upload and get the video URL
                video_uri = response.json().get('uri')
                if not video_uri:
                    raise ValidationError("Failed to get video URI from Vimeo")
                
                # Ensure the video URI includes the scheme
                if not video_uri.startswith('https://'):
                    video_uri = f'https://api.vimeo.com{video_uri}'
                
                video_data = requests.get(video_uri, headers={
                    'Authorization': f'bearer {settings.VIMEO_ACCESS_TOKEN}',
                    'Accept': 'application/vnd.vimeo.*+json;version=3.4'
                }).json()
                
                obj.video_url = video_data.get('link')
                
                if not obj.video_url:
                    raise ValidationError("Failed to get video URL from Vimeo")
                
                
                
            except Exception as e:
                raise ValidationError(f"Vimeo upload failed: {str(e)}")
        
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # Ensure the video URL exists (and thus was uploaded to Vimeo)
        if obj.video_url:
            try:
                # Extract the Vimeo video ID from the URL
                video_id = obj.video_url.split('/')[-1]
                
                # Make the DELETE request to Vimeo to remove the video
                delete_url = f"https://api.vimeo.com/videos/{video_id}"
                headers = {
                    'Authorization': f'bearer {settings.VIMEO_ACCESS_TOKEN}',
                    'Accept': 'application/vnd.vimeo.*+json;version=3.4'
                }
                
                response = requests.delete(delete_url, headers=headers)
                
                if response.status_code != 204:
                    raise ValidationError(f"Failed to delete video on Vimeo: {response.json().get('error', response.text)}")

            except Exception as e:
                raise ValidationError(f"Failed to delete video from Vimeo: {str(e)}")

        # Call the superclass method to delete the video record in the Django database
        super().delete_model(request, obj)




class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'is_enroll', 'enroll_date')
    list_filter = ('is_enroll', 'enroll_date')
    search_fields = ('user__email', 'course__title')
    ordering = ('-enroll_date',)
    readonly_fields = ('enroll_date',)

    def has_add_permission(self, request):
        # Optional: Restrict adding new enrollments from the admin panel
        return False

    def has_change_permission(self, request, obj=None):
        # Optional: Restrict changing enrollments from the admin panel
        return True

    def has_delete_permission(self, request, obj=None):
        # Optional: Restrict deleting enrollments from the admin panel
        return False

admin.site.register(Enrollment, EnrollmentAdmin)            



class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at', 'user', 'video')
    search_fields = ('user__email', 'video__title')
    ordering = ('-completed_at',)

admin.site.register(VideoProgress, VideoProgressAdmin)






