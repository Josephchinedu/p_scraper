from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class ScrapedData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    data = models.JSONField()
    keywords = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SCRAPED DATA"
        verbose_name_plural = "SCRAPED DATA"

    def __str__(self):
        return f"{self.user.username} - {self.url}"
