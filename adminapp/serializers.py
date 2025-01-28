from testapp.models import User, ParentProfile, StudentProfile, TeacherProfile, ParentStudentMapping
from rest_framework import serializers
from django.contrib.auth.hashers import make_password


# class AdminUserCreationSerializer(serializers.ModelSerializer):
#     password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
#     student_ids = serializers.ListField(
#         child=serializers.IntegerField(),
#         required=False,
#         write_only=True,
#         help_text="List of student IDs to associate with the parent"
#     )

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'password2', 'role', 'phone_number', 'is_approved', 'student_ids']
#         extra_kwargs = {
#             'password': {'write_only': True, 'style': {'input_type': 'password'}},
#         }

#     def validate(self, attrs):
#         password = attrs.get('password')
#         password2 = attrs.get('password2')
#         email = attrs.get('email')
#         role = attrs.get('role')
#         student_ids = attrs.get('student_ids', [])

#         # Email uniqueness check
#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError({'email': 'Email is already taken.'})

#         # Password validation
#         if password != password2:
#             raise serializers.ValidationError({"password": "Passwords do not match."})

#         # Role validation
#         if role not in ['teacher', 'student', 'parent', 'guest', 'admin']:
#             raise serializers.ValidationError({"role": "Invalid role specified."})

#         # Parent-specific validation
#         if role == 'parent' and student_ids:
#             # Ensure all provided student IDs exist and are valid
#             for student_id in student_ids:
#                 if not User.objects.filter(id=student_id, role='student').exists():
#                     raise serializers.ValidationError({"student_ids": f"Invalid student ID: {student_id}"})

#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('password2')
#         student_ids = validated_data.pop('student_ids', [])
#         validated_data['password'] = make_password(validated_data['password'])

#         # Create the user
#         user = User.objects.create(**validated_data)

#         # Create corresponding profile if `is_approved` is True
#         if validated_data.get('is_approved'):
#             if validated_data['role'] == 'student':
#                 StudentProfile.objects.create(user=user, enrollment_date=None)
#             elif validated_data['role'] == 'parent':
#                 parent_profile = ParentProfile.objects.create(user=user, relationship="Guardian")
#                 for student_id in student_ids:
#                     student_profile = StudentProfile.objects.get(user_id=student_id)
#                     ParentStudentMapping.objects.create(parent=parent_profile, student=student_profile)
#             elif validated_data['role'] == 'teacher':
#                 TeacherProfile.objects.create(user=user, enrollment_date=None)

#         return user

class AdminUserCreationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of student IDs to associate with the parent"
    )
    relationship = serializers.CharField(
        required=False, 
        write_only=True, 
        help_text="Relationship for parent role (e.g., Father, Mother, Guardian)"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role', 'phone_number', 'is_approved', 'student_ids', 'relationship']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        email = attrs.get('email')
        role = attrs.get('role')
        student_ids = attrs.get('student_ids', [])
        relationship = attrs.get('relationship', None)

        # Email uniqueness check
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email is already taken.'})

        # Password validation
        if password != password2:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Role validation
        if role not in ['teacher', 'student', 'parent', 'guest', 'admin']:
            raise serializers.ValidationError({"role": "Invalid role specified."})

        # Parent-specific validation
        if role == 'parent':
            # Ensure relationship is provided for parent role
            if not relationship:
                raise serializers.ValidationError({"relationship": "Relationship is required for parent role."})

            # Ensure all provided student IDs exist and are valid
            for student_id in student_ids:
                if not User.objects.filter(id=student_id, role='student').exists():
                    raise serializers.ValidationError({"student_ids": f"Invalid student ID: {student_id}"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        student_ids = validated_data.pop('student_ids', [])
        relationship = validated_data.pop('relationship', None)
        validated_data['password'] = make_password(validated_data['password'])

        # Create the user
        user = User.objects.create(**validated_data)

        # Create corresponding profile if `is_approved` is True
        if validated_data.get('is_approved'):
            if validated_data['role'] == 'student':
                StudentProfile.objects.create(user=user, enrollment_date=None)
            elif validated_data['role'] == 'parent':
                # Use the relationship provided by the admin
                parent_profile = ParentProfile.objects.create(user=user, relationship=relationship)
                for student_id in student_ids:
                    student_profile = StudentProfile.objects.get(user_id=student_id)
                    ParentStudentMapping.objects.create(parent=parent_profile, student=student_profile)
            elif validated_data['role'] == 'teacher':
                TeacherProfile.objects.create(user=user, enrollment_date=None)

        return user



# # Edit user
class AdminUserEditSerializer(serializers.ModelSerializer):
    """
    Serializer for editing user details at the admin level with role-based logic, 
    including editing parent-student mappings.
    """
    # Optional fields for role-specific data
    relationship = serializers.CharField(required=False, write_only=True, help_text="Relationship for parent role")
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of student IDs to associate with the parent"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_approved', 'phone_number', 'relationship', 'student_ids']

    def validate(self, attrs):
        role = attrs.get('role', None)
        student_ids = attrs.get('student_ids', [])

        # Role-specific validations
        if role == 'parent':
            if 'relationship' not in attrs:
                raise serializers.ValidationError({"relationship": "Relationship is required for parent role."})

            # Validate student IDs if provided
            for student_id in student_ids:
                if not User.objects.filter(id=student_id, role='student').exists():
                    raise serializers.ValidationError({"student_ids": f"Invalid student ID: {student_id}"})

        return attrs

    def update(self, instance, validated_data):
        # General user updates
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.is_approved = validated_data.get('is_approved', instance.is_approved)

        # Role-specific updates
        role = validated_data.get('role', instance.role)
        instance.role = role

        # Handle role-based profile updates
        if role == 'parent':
            # Update relationship
            relationship = validated_data.get('relationship')
            parent_profile, created = ParentProfile.objects.get_or_create(user=instance)
            parent_profile.relationship = relationship
            parent_profile.save()

            # Update parent-student mapping
            student_ids = validated_data.get('student_ids', [])
            if student_ids:
                # Remove old mappings
                ParentStudentMapping.objects.filter(parent=parent_profile).delete()

                # Create new mappings
                for student_id in student_ids:
                    student_profile = StudentProfile.objects.get(user_id=student_id)
                    ParentStudentMapping.objects.create(parent=parent_profile, student=student_profile)

        elif role == 'student':
            student_profile, created = StudentProfile.objects.get_or_create(user=instance)
            student_profile.save()
        elif role == 'teacher':
            teacher_profile, created = TeacherProfile.objects.get_or_create(user=instance)
            teacher_profile.save()

        instance.save()
        return instance



class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to include user-specific data along with role-based details.
    """

    role_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_approved', 'phone_number', 'role_data']

    def get_role_data(self, obj):
        # Add role-specific fields dynamically
        if obj.role == 'student' and hasattr(obj, 'student_profile'):
            return {
                "enrollment_date": obj.student_profile.enrollment_date,
            }
        # elif obj.role == 'parent' and hasattr(obj, 'parent_profile'):
        #     return {
        #         "relationship": obj.parent_profile.relationship,
        #     }
        elif obj.role == 'parent' and hasattr(obj, 'parent_profile'):
            # Get all student profiles mapped to this parent
            parent_profile = obj.parent_profile
            mapped_students = ParentStudentMapping.objects.filter(parent=parent_profile).select_related('student__user')

            # Serialize student details
            students = [
                {
                    "id": mapping.student.user.id,
                    "username": mapping.student.user.username,
                    "email": mapping.student.user.email,
                    "enrollment_date": mapping.student.enrollment_date,
                }
                for mapping in mapped_students
            ]

            return {
                "relationship": parent_profile.relationship,
                "students": students
            }
        elif obj.role == 'teacher' and hasattr(obj, 'teacher_profile'):
            return {
                "enrollment_date": obj.teacher_profile.enrollment_date,
            }
        return None


