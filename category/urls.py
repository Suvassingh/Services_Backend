from django.urls import path
from .views import (
    get_categories,
    get_services_by_category,
    add_category,
    add_product,
    get_products_by_category,
    upload_image,
    get_all_products,
    get_vendor_products,
    get_featured_products,
    update_product,
    delete_product,
    get_product_detail,toggle_like,product_like_status,get_liked_products
)

urlpatterns = [
    path('', get_categories, name='categories_root'),  
    path('categories/', get_categories, name='get_categories'),
    path('services/<int:category_id>/', get_services_by_category, name='get_services_by_category'),
    path('add/', add_category, name='add_category'),
    path('product/add/<int:category_id>/', add_product, name='add_product'),
    path('products/<int:category_id>/', get_products_by_category, name='get_products_by_category'),
    path('products/', get_all_products, name='get_all_products'),
    path('vendor/products/', get_vendor_products, name='get_vendor_products'),
    path('products/featured/', get_featured_products, name='get_featured_products'),
    path('product/<int:pk>/update/', update_product, name='update_product'),
    path('product/<int:pk>/delete/', delete_product, name='delete_product'),
    path('product/<int:pk>/', get_product_detail, name='get_product_detail'),
    path('upload/', upload_image, name='upload_image'),
    path("toggle-like/", toggle_like, name="toggle_like"),
    path("like-status/<int:product_id>/", product_like_status, name="product_like_status"),
    path("liked-products/",get_liked_products,name="get_liked_products"),
]
