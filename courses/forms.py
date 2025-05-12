from django import forms
from .models import Course
from .models import Quiz, Question, Option

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

    # Optional: Add custom validation or field-specific logic here if needed
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")
        return title

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'available_from', 'available_until', 'due_date', 'time_limit']
        widgets = {
            'available_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'available_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[str(field)].widget.attrs.update(placeholder=f'Enter quiz {str(field)}')
        self.fields['time_limit'].widget.attrs.update(placeholder=f'Enter time limit')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['type', 'text', 'points', 'order', 'correct_answer']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'correct_answer': forms.Textarea(attrs={'rows': 2}),
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
