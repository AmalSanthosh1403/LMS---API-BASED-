from .models import User
from rest_framework import serializers

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


# registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('guest', 'Guest')
    ], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        email = attrs.get('email')
        role = attrs.get('role')

        if role == 'parent':
            raise serializers.ValidationError({"role": "Only admins can create Parent users."})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email is already taken.'})
            
        if password != password2:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)

# login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, 
        error_messages={
            'blank': 'Username cannot be empty.',
            'required': 'Username is required.'
        }
    )
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        error_messages={
            'blank': 'Password cannot be empty.',
            'required': 'Password is required.'
        }
    )

    def validate(self, attrs):
        User = get_user_model()
        username = attrs.get('username')
        password = attrs.get('password')

        # Check if username and password are provided
        if not username or not password:
            raise serializers.ValidationError({
                'error': 'Both username and password are required.'
            })

        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'User not found...'
            })

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({
                'error': 'Incorrect password.'
            })

        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError({
                'error': 'User account is not active.'
            })

        if not user.is_approved:
            raise serializers.ValidationError({
                'error': 'User account is not approved.'
            })
        
        attrs['user'] = user
        return attrs
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            # Blacklist the refresh token
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError('Invalid or expired token')
