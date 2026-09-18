from django.contrib import admin
from .models import Category, SubCategory, Brand, Size, Color, Product, ProductVariant


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubCategoryInline]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("label", "display_order")


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    readonly_fields = ("sku", "barcode")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "subcategory", "gender", "brand",
                     "selling_price", "total_stock_display", "is_active")
    list_filter = ("category", "gender", "brand", "is_active", "is_new_arrival", "is_best_seller")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductVariantInline]

    def total_stock_display(self, obj):
        return obj.total_stock
    total_stock_display.short_description = "Stock"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "color", "sku", "barcode", "stock_quantity")
    list_filter = ("size", "color")
    search_fields = ("sku", "barcode", "product__name")
    readonly_fields = ("sku", "barcode")
