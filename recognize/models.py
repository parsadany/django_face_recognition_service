from django.db import models

# Create your models here.


class Profile(models.Model):
    matching_id = models.BigIntegerField(unique=True)

class KnownImage(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    url = models.URLField()
    is_active = models.BooleanField(blank=True, default=True)


