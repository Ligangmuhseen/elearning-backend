import uuid
from django.db import models
from account.models import CustomUser
from django.core.exceptions import ValidationError

class Course(models.Model):
    course_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    cover_image = models.ImageField(upload_to='courses/covers/', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_posted = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Chapter(models.Model):
    chapter_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} of {self.course.title}"

class Videos(models.Model):
    video_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)  # Allow video_url to be empty
    uploaded_at = models.DateField(auto_now_add=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    # course = models.ForeignKey(Course, on_delete=models.CASCADE)


    class Meta:
        verbose_name ='Video'
        verbose_name_plural = 'Videos'


    def __str__(self):
        return f"{self.title}-{self.video_url}"    
        


class VideoProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video = models.ForeignKey(Videos, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'video')  # Ensures one record per user/video pair

    def __str__(self):
        return f"{self.user.email} - {self.video.title} - Completed: {self.is_completed}"    

    

    class Meta:
        verbose_name = 'VideoProgress'
        verbose_name_plural = 'VideosProgresses'


    

class Enrollment(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_enroll = models.BooleanField(default=False)
    enroll_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}" 

        






