# Generated by Django 5.2.1 on 2025-05-11 15:09

import datetime
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseenrollment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='courses.course'),
        ),
        migrations.CreateModel(
            name='CourseInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invitation_code', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('expiration_date', models.DateTimeField(default=datetime.datetime(2025, 5, 11, 18, 9, 16, 334380, tzinfo=datetime.timezone.utc))),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('inviter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_sent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
