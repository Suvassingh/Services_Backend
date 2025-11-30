from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Category, Service
from .serializers import CategorySerializer, ServiceSerializer
from rest_framework import status
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
        serializer.save()   # 👉 This stores category into MySQL
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)