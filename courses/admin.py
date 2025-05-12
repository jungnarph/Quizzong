from django.contrib import admin
from .models import Course, CourseEnrollment, CourseInvitation
from .models import Quiz, Question, Option

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    list_filter = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only auto-enroll the owner if this is a new course (not updated)
            obj.owner = request.user
            super().save_model(request, obj, form, change)

            # Auto-enroll the course owner
            CourseEnrollment.objects.get_or_create(
                user=request.user,
                course=obj,
                defaults={'enrolled_at': obj.created_at}
            )
        else:
            super().save_model(request, obj, form, change)

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('enrolled_at',)

@admin.register(CourseInvitation)
class CourseInvitationAdmin(admin.ModelAdmin):
    list_display = ('course', 'inviter', 'invitation_code', 'expiration_date', 'is_valid')
    search_fields = ('course__title', 'inviter__username', 'invitation_code')
    list_filter = ('expiration_date',)

    def is_valid(self, obj):
        return obj.is_valid()

    is_valid.boolean = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    # Use the ManyToManyField widget automatically
    filter_horizontal = ('questions',)  # Optional: adds a filter widget
    list_display = ('title',)  # List the quiz title in the admin list

# Register the Question model if needed
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text',)

