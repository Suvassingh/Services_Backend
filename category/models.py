import hashlib
from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4


# class Category(models.Model):
#     title = models.CharField(max_length=100)
#     icon = models.ImageField(upload_to="category_icons/", null=True, blank=True)

#     def __str__(self):
#         return self.title


# class Service(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services")
#     name = models.CharField(max_length=200)
#     description = models.TextField(null=True, blank=True)
#     image = models.ImageField(upload_to="service_images/", null=True, blank=True)
#     rating = models.FloatField(default=0.0)

#     def __str__(self):
#         return self.name




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


class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="products")
   
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.CharField(max_length=50)
    vendorId = models.CharField(max_length=255, blank=True)
    vendorName = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    images = models.JSONField(default=list, blank=True)
    rating = models.FloatField(default=4.0)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user and not self.vendorId:
            self.vendorId = hashlib.sha256(str(self.user.id).encode()).hexdigest()
        if not self.vendorId:
            self.vendorId = hashlib.sha256(str(uuid4()).encode()).hexdigest()
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title




class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'product')  

    def __str__(self):
        return f"{self.user} - {self.product} - {self.liked}"