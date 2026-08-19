from django import forms
from .models import Assignment, Submission

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "due_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["text", "file"]
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["score", "max_score", "feedback"]
        widgets = {
            "score": forms.NumberInput(attrs={"class": "form-control", "step": "0.5"}),
            "max_score": forms.NumberInput(attrs={"class": "form-control", "step": "0.5"}),
            "feedback": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
