from django.contrib import admin
from .models import User, StudentProfile, TeacherProfile, ParentProfile, ParentStudentMapping


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'date_joined')  # Columns to display
    list_filter = ('role',)  # Add filter for roles (e.g., Parent, Student, Admin, etc.)
    search_fields = ('username', 'email')  # Optional: Search users by username or email


# Register other models without customization
admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(ParentProfile)
admin.site.register(ParentStudentMapping)
