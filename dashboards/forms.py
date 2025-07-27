from django import forms
from .models import Lesson

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'lesson_type', 'max_students', 'duration_weeks', 'duration_hours', 'start_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter lesson title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter lesson description'
            }),
            'lesson_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'max_students': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Max number of students'
            }),
            'duration_weeks': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in weeks'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in hours'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'placeholder': 'Select start date and time'
            }),
        }
