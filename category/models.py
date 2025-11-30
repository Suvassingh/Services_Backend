from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="category_icons/", null=True, blank=True)

    def __str__(self):
        return self.title


class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="service_images/", null=True, blank=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.name
