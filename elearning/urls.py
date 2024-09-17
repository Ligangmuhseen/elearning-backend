from django.urls import path
from . import views


urlpatterns = [
    path('courses/', views.CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<uuid:pk>/', views.CourseDetailView.as_view(), name='course-list-create'),
    path('courses/latest/', views.LatestCoursesView.as_view(), name='latest-courses'),
    path('enroll/<uuid:course_id>/', views.enroll_user, name='enroll_user'),
    path('user/enrollments/', views.UserEnrollmentsView.as_view(), name='user-enrollments'),
    path('courses/<uuid:course_id>/chapters-videos/', views.course_chapters_videos, name='course_chapters_videos'),
    path('video/<uuid:video_id>/complete/', views.mark_video_completed, name='mark_video_completed'),
    
]