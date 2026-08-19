from django import forms
from .models import Quiz, Question

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "description", "time_limit_minutes"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "time_limit_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "option_a", "option_b", "option_c", "option_d", "correct_answer"]
        widgets = {f: forms.TextInput(attrs={"class": "form-control"}) for f in ["option_a","option_b","option_c","option_d"]}
        widgets["text"] = forms.Textarea(attrs={"class": "form-control", "rows": 2})
        widgets["correct_answer"] = forms.Select(attrs={"class": "form-select"})
