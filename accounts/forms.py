from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User

DEFAULT_STUDENT_PASSWORD = "AIT@2026"
DEFAULT_INSTRUCTOR_PASSWORD = "AITSTAFF@2026"


class StudentSignUpForm(forms.ModelForm):
    """
    Any student can sign up using their index/student ID number.
    No pre-loaded registry needed — just enter your ID and details.
    """
    first_name = forms.CharField(max_length=150, required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}))
    last_name = forms.CharField(max_length=150, required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}))
    student_id = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "ADS21B00022Y"}))
    semester = forms.ChoiceField(
        choices=[(i, f"Semester {i}") for i in range(1, 9)],
        widget=forms.Select(attrs={"class": "form-select"}))
    department = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Computer Science"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "student_id", "semester", "department"]

    def clean_student_id(self):
        sid = self.cleaned_data["student_id"].strip()
        if User.objects.filter(student_id=sid).exists():
            raise forms.ValidationError(
                "An account already exists for this Student ID. Please log in instead."
            )
        if User.objects.filter(username=sid).exists():
            raise forms.ValidationError(
                "This Student ID is already taken. Please log in instead."
            )
        return sid

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data["student_id"],
            student_id=self.cleaned_data["student_id"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            department=self.cleaned_data.get("department", ""),
            semester=self.cleaned_data["semester"],
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
    csv_file = forms.FileField(
        label="Student Registry CSV File",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".csv"})
    )