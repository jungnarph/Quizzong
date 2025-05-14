from django import forms
from django.contrib.auth.models import User
from .models import Message
from courses.models import Course

class MessageForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.none(), required=True)

    class Meta:
        model = Message
        fields = ['course', 'recipient', 'subject', 'body']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['course'].queryset = Course.objects.filter(students=user)

            if 'course' in self.data:
                try:
                    course_id = int(self.data.get('course'))
                    course = Course.objects.get(id=course_id)
                    self.fields['recipient'].queryset = course.students.exclude(id=user.id)
                except (ValueError, Course.DoesNotExist):
                    self.fields['recipient'].queryset = User.objects.none()
            elif self.instance.pk:
                course = self.instance.course
                self.fields['recipient'].queryset = course.students.exclude(id=user.id)
            else:
                self.fields['recipient'].queryset = User.objects.none()
