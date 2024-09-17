from rest_framework import serializers
from .models import Course, Enrollment,Videos,Chapter,VideoProgress



class VideoSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Videos
        fields = ['video_id', 'title', 'description', 'video_url', 'uploaded_at', 'is_completed']

    def get_is_completed(self, obj):
        # Get the request context to access the user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if there is a progress entry for the user and this video
            progress = VideoProgress.objects.filter(user=request.user, video=obj).first()
            return progress.is_completed if progress else False
        return False




class ChapterSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True, source='videos_set')

    class Meta:
        model = Chapter
        fields = ['chapter_id', 'title', 'description', 'videos']



class CourseSerializer(serializers.ModelSerializer):
    # chapters = ChapterSerializer(many=True, read_only=True, source='chapter_set')
    is_enroll = serializers.SerializerMethodField()  # Add custom field to check if the user is enrolled

    class Meta:
        model = Course
        fields = '__all__'  # Include all fields + is_enroll

    def get_is_enroll(self, obj):
        
        user = self.context.get('request').user # Get the authenticated user from the request context
        # print('user is',user)
        if user.is_authenticated:
            # Check if the user is enrolled in this course
            return Enrollment.objects.filter(course=obj, user=user).exists()
        return False
    

class EnrollmentSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    course_description = serializers.SerializerMethodField()
    course_image = serializers.SerializerMethodField()



    class Meta:
        model = Enrollment
        fields = '__all__'



    def get_course_name(self, obj):
        return obj.course.title


    def get_course_description(self, obj):  
        return obj.course.description


    def get_course_image(self,obj):
        return obj.course.cover_image.url
    







