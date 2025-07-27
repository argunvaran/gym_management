from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class Skill(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('manager', 'Manager'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    skills = models.ManyToManyField(Skill, blank=True)  # Yalnızca öğretmenler için beceri alanı

    def is_manager(self):
        return self.role == 'manager'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    def clean(self):
        # Yalnızca öğretmen olmayan kullanıcılar için skills alanının boş olmasını sağla
        if self.role != 'teacher' and self.skills.exists():
            raise ValidationError("Only teachers can have skills.")

