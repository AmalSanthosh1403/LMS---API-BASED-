from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from testapp.serializers import UserRegistrationSerializer
from .serializers import AdminUserCreationSerializer, AdminUserEditSerializer, UserProfileSerializer
from testapp.models import User
from django.views.decorators.csrf import csrf_exempt


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure only admins can access
def create_user(request):
    """
    Allows admins to create users of specific roles (e.g., teacher, parent, student).
    """
    if request.user.role != 'admin':
        return Response({"error": "You do not have permission to create users."}, status=status.HTTP_403_FORBIDDEN)

    serializer = AdminUserCreationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": f"{user.role.capitalize()} created successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # View users or single user
@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users
def user_management(request):
    """
    Admin-only endpoint to list all users or view a single user's details.
    """
    # Ensure only admins can access this functionality
    if request.user.role != 'admin':
        return Response({"error": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)

    # If `user_id` is provided, fetch details of a single user
    user_id = request.data.get('id', None)
    if user_id is not None:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # # For updating user data
        if request.method == 'PUT':
            serializer = AdminUserEditSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                updated_user = serializer.save()
                return Response({
                    "message": "User updated successfully!",
                    "user": AdminUserEditSerializer(updated_user).data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    is_approved = request.data.get('is_approved', None)
    if is_approved is not None:  # Filter by `is_approved`
        users = User.objects.filter(is_approved=is_approved)
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Otherwise, list all users
    users = User.objects.all()
    serializer = UserProfileSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
