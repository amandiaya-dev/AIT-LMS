from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentRecord


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "student_id", "get_full_name", "role", "semester", "department", "is_staff")
    list_filter = ("role", "semester", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("LMS Profile", {"fields": ("role", "student_id", "semester", "department", "profile_picture")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("LMS Role", {"fields": ("role", "student_id", "semester", "department")}),
    )


@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ("student_id", "first_name", "last_name", "semester", "department", "is_active", "imported_at")
    list_filter = ("is_active", "semester", "department")
    search_fields = ("student_id", "first_name", "last_name")


admin.site.register(User, CustomUserAdmin)
