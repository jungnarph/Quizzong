from django import forms
from django.forms import inlineformset_factory
from .models import Course
from .models import Quiz, Question, Option
from taggit.forms import TagField

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
        fields = ['course', 'title', 'description', 'available_from', 'available_until', 'due_date', 'time_limit']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'available_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'available_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)  # get course passed in from view
        super().__init__(*args, **kwargs)
        print(course)
        if course:
            self.fields['course'].initial = course
            self.fields['course'].queryset = Course.objects.filter(pk=course.pk)
            self.fields['course'].disabled = True

        for field in self.fields:
            self.fields[str(field)].widget.attrs.update(placeholder=f'Enter quiz {str(field)}')
        self.fields['time_limit'].widget.attrs.update(placeholder=f'Enter time limit')


class QuestionForm(forms.ModelForm):
    tags = TagField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Add tags (comma-separated)'
    }))

    class Meta:
        model = Question
        fields = ['type', 'text', 'points', 'order', 'correct_answer', 'tags']

        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'rows': 3}),
            'correct_answer': forms.Textarea(attrs={'rows': 1}),
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if not tags:
            raise forms.ValidationError("Each question must have at least one tag.")
        return tags

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']

OptionFormSet = inlineformset_factory(
    Question, Option, form=OptionForm,
    extra=2, min_num=1, validate_min=True, can_delete=True
)

