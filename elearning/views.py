from rest_framework import generics
from .models import Course,Chapter,Videos,VideoProgress
from .serializers import CourseSerializer,VideoSerializer
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from .models import Course, Enrollment
from rest_framework.decorators import  permission_classes,api_view
from rest_framework.permissions import IsAuthenticated,AllowAny
from account.models import CustomUser
from .serializers import EnrollmentSerializer,ChapterSerializer



class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]  # Allow any user to view course details 

    def get_serializer_context(self):
        """
        Add request to the serializer context.
        """
        return {'request': self.request}   


class LatestCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.all().order_by('-date_posted')[:6]
    

# return chapters with associated videos of single course
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_chapters_videos(request, course_id):
    try:
        course = Course.objects.get(course_id=course_id)
        chapters = Chapter.objects.filter(course=course)
        serialized_chapters = ChapterSerializer(chapters, many=True, context={'request': request})
        return Response({'course': course.title, 'chapters': serialized_chapters.data})
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=404)  



@permission_classes([IsAuthenticated])
@api_view(['POST'])
def enroll_user(request, course_id):
    """
    Enroll the user in a specific course if they are not already enrolled.
    """
    userid = request.user.userid  # Assuming the user is authenticated

    # Get the course by its UUID
    course = get_object_or_404(Course, course_id=course_id)

    # Get the user by its UUID
    user = get_object_or_404(CustomUser, userid=userid)

    # Check if the user is already enrolled
    enrollment, created = Enrollment.objects.get_or_create(course=course, user=user)

    if not created:
        # User is already enrolled in the course
        return JsonResponse({
            'status': 'failed',
            'message': 'You are already enrolled in this course.'
        })

    # If newly created, enroll the user
    enrollment.is_enroll = True
    enrollment.save()

    return JsonResponse({
        'status': 'success',
        'message': f'Successfully enrolled in {course.title}.'
    })   




class UserEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def get_queryset(self):
        # Return enrollments that belong to the currently authenticated user
        return Enrollment.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Get the queryset (enrollments of the current user)
        queryset = self.get_queryset()

        # Serialize the data
        serializer = self.get_serializer(queryset, many=True)

        # Create a custom response including the count of enrollments
        return Response({
            "enrollments": serializer.data,
            "count": queryset.count()
        })
    



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_video_completed(request, video_id):
    user = request.user
    try:
        video = Videos.objects.get(video_id=video_id)
        # Get or create a progress record for this user and video
        progress, created = VideoProgress.objects.get_or_create(user=user, video=video)
        
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()

        return Response({"message": "Video marked as completed."}, status=status.HTTP_200_OK)
    
    except Videos.DoesNotExist:
        return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)
