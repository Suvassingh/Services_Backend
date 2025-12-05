from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from .models import Category, Service, Product
from .serializers import CategorySerializer, ServiceSerializer, ProductSerializer
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_services_by_category(request, category_id):
    services = Service.objects.filter(category_id=category_id)
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_product(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['category'] = category_id   

    serializer = ProductSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    if 'image' not in request.FILES:
        return Response({"error": "No image provided"}, status=400)
    
    image_file = request.FILES['image']
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_{timestamp}_{image_file.name}"
    
    
    save_path = os.path.join(settings.MEDIA_ROOT, 'product_images', filename)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)
    
    image_url = f"{settings.MEDIA_URL}product_images/{filename}"
    
    return Response({"image_url": image_url}, status=200)

@api_view(['GET'])
def get_all_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
