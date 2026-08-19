from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User, StudentRecord

DEFAULT_STUDENT_PASSWORD = "AIT@2026"
DEFAULT_INSTRUCTOR_PASSWORD = "AITSTAFF@2026"


class StudentSignUpForm(forms.ModelForm):
    """
    Students sign up using their Student ID.
    The ID is verified against the StudentRecord registry before the
    account is created. If not found or inactive, signup is blocked.
    Name, semester and department are auto-filled from the registry.
    """
    student_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "e.g. AIT/2024/001"
        })
    )

    class Meta:
        model = User
        fields = ["student_id"]

    def clean_student_id(self):
        sid = self.cleaned_data["student_id"].strip()

        # Check registry
        try:
            record = StudentRecord.objects.get(student_id=sid, is_active=True)
        except StudentRecord.DoesNotExist:
            raise forms.ValidationError(
                "This Student ID was not found in the AIT registry. "
                "Please check your ID or contact the administration."
            )

        # Check not already registered
        if User.objects.filter(student_id=sid).exists():
            raise forms.ValidationError(
                "An account already exists for this Student ID. "
                "Please log in instead."
            )

        # Attach record to use in save()
        self._registry_record = record
        return sid

    def save(self, commit=True):
        record = self._registry_record
        user = User(
            username=record.student_id,
            student_id=record.student_id,
            first_name=record.first_name,
            last_name=record.last_name,
            department=record.department,
            semester=record.semester,
            role=User.Role.STUDENT,
        )
        user.set_password(DEFAULT_STUDENT_PASSWORD)
        if commit:
            user.save()
        return user


class InstructorSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=150, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}))
    department = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "department", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["username", "password1", "password2"]:
            self.fields[field_name].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.INSTRUCTOR
        user.department = self.cleaned_data.get("department", "")
        if commit:
            user.save()
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class CSVImportForm(forms.Form):
    """Admin uploads a CSV file of student records."""
    csv_file = forms.FileField(
        label="Student Registry CSV File",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".csv"})
    )
