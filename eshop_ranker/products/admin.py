from django.contrib import admin
from products.models import Product,ProductListing

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'brand',
        'category',
        'subcategory',
        'is_active',
        'created_at',
    )

    list_filter = ('category','subcategory','is_active')
    search_fields = ('name','brand','category')

@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'source',
        'price',
        'product_url',
        'last_updated',
    )