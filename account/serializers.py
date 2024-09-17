from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ('userid', 'email', 'first_name', 'last_name', 'password','phone_no', 'gender', 'role', 'is_active', 'date_joined', 'last_login')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
      
        
        # Create user with the validated data
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_no = validated_data['phone_no'],
            role=validated_data['role'],
            gender=validated_data['gender'],
            
         
        )
        return user