from django.urls import path
from .views import get_categories, get_services_by_category,add_category,add_product,get_products_by_category

urlpatterns = [
    path('categories/', get_categories),
    path('services/<int:category_id>/', get_services_by_category),
    path('add/', add_category),
    path('product/add/<int:category_id>/', add_product),
    path('products/<int:category_id>/', get_products_by_category),
]
