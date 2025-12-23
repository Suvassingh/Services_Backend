from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Category, Service, Product, ProductLike
from .serializers import CategorySerializer, ServiceSerializer, ProductSerializer

from datetime import datetime
import os, json
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.storage import default_storage

@api_view(['POST'])
def add_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
@parser_classes([JSONParser, MultiPartParser, FormParser])
def add_product(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['category'] = category.id

    images_field = data.get('images')
    if isinstance(images_field, str):
        try:
            data['images'] = json.loads(images_field)
        except json.JSONDecodeError:
            data['images'] = [images_field]

    serializer = ProductSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        user = request.user if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser) and request.user.is_authenticated else None
        product = serializer.save(user=user)
        response_serializer = ProductSerializer(product, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
# def upload_image(request):
 
#     if 'image' not in request.FILES:
#         return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

#     image_file = request.FILES['image']
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"product_{timestamp}_{image_file.name}"

#     save_subdir = "product_images"
#     save_path = os.path.join(save_subdir, filename)

#     full_path = default_storage.save(save_path, image_file)

#     image_url = f"{settings.MEDIA_URL}{full_path}"
#     return Response({"image_url": image_url}, status=status.HTTP_200_OK)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    images = request.FILES.getlist('image')

    if not images:
        return Response({"error": "No images provided"}, status=400)

    image_urls = []

    for image_file in images:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"product_{timestamp}_{image_file.name}"

        save_subdir = "product_images"
        save_path = os.path.join(save_subdir, filename)

        full_path = default_storage.save(save_path, image_file)
        image_url = f"{settings.MEDIA_URL}{full_path}"

        image_urls.append(image_url)

    return Response(
        {"image_urls": image_urls},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def get_products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_vendor_products(request):
    current_user = request.user
    products = Product.objects.filter(user_id=current_user)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)




@api_view(['GET'])
def get_featured_products(request):
    products = Product.objects.filter(featured=True)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def update_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if product.user_id != request.user.id:
        return Response({"error": "You are not allowed to update this product"}, status=status.HTTP_403_FORBIDDEN)

    serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()  
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
def delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if product.user_id != request.user.id:
        return Response({"error": "You are not allowed to delete this product"}, status=status.HTTP_403_FORBIDDEN)

    product.delete()
    return Response({"message": "Product deleted successfully"}, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductSerializer(product)
    return Response(serializer.data)




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_like(request):
    product_id = request.data.get("product_id")

    if not product_id:
        return Response({"error": "Missing product_id"}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Invalid product"}, status=400)

    like_obj, created = ProductLike.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"liked": True}
    )

    if not created:
        like_obj.liked = not like_obj.liked
        like_obj.save()

    return Response({"liked": like_obj.liked}, status=200)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_like_status(request, product_id):
    liked = ProductLike.objects.filter(user=request.user, product_id=product_id, liked=True).exists()
    return Response({"liked": liked})



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_liked_products(request):
    liked_products = Product.objects.filter(
        productlike__user=request.user,
        productlike__liked=True
    )
    serializer = ProductSerializer(liked_products, many=True, context={'request': request})
    return Response(serializer.data)