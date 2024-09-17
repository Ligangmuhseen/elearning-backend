
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login,logout
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView



class UserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': 'User registered successfully',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            # Generate or retrieve the token
            token, created = Token.objects.get_or_create(user=user)
            # Include user's role and token in the response
            response_data = {
                'message': 'Login successful',
                'role': user.role,
                'token': token.key,  # Include the token in the response data
                'userid': user.userid
            }
            # Check user's role and return appropriate response
            if user.role == 'admin':
                response_data['message'] = 'Admin login successful'
            elif user.role == 'client':
                response_data['message'] = 'Client login successful'
          
            else:
                response_data['message'] = 'Unknown role'
                return Response(response_data, status=status.HTTP_403_FORBIDDEN)

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)  




class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})



# fetch the detail specific to a user
class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get the logged-in user
        user = self.request.user
        return user

