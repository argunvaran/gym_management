from django.db import models
from dashboards.models import Lesson

class TestModel(models.Model):
    name = models.CharField(max_length=100)
    related_model = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="test_models")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
