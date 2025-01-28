from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('guest', 'Guest'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile_images/', default='default/default_profile.jpg', blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    enrollment_date =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    relationship = models.CharField(max_length=20)  # e.g., Father, Mother, Guardian

    def __str__(self):
        return f"{self.user.username} ({self.relationship})"
    

class ParentStudentMapping(models.Model):
    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name='student_mappings'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='parent_mappings'
    )

    def __str__(self):
        return f"{self.parent.user.username} -> {self.student.user.username} ({self.parent.relationship}) "




class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    enrollment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

