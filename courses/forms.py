from django import forms
from .models import Course
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "semester"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "semester": forms.Select(attrs={"class": "form-select"}),
        }
