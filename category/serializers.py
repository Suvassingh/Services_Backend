from rest_framework import serializers
from .models import Category, Service,Product
import hashlib


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'icon']
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'category', 'name', 'description', 'image', 'rating']
        
class ProductSerializer(serializers.ModelSerializer):
    # Expose vendorId as read-only (server generates if not provided)
    vendorId = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'user', 'title', 'description', 'price', 'vendorId',
            'vendorName', 'location', 'contact', 'images', 'rating', 'featured', 'created_at'
        ]
        read_only_fields = ['vendorId', 'created_at']

  