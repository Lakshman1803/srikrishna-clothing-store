from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Top level: MEN, WOMEN, BOYS, GIRLS, KIDS"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon for quick display")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=70)

    class Meta:
        verbose_name_plural = "Sub Categories"
        unique_together = ("category", "slug")
        ordering = ["name"]

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class Brand(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Size(models.Model):
    label = models.CharField(max_length=30, unique=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "label"]

    def __str__(self):
        return self.label


class Color(models.Model):
    name = models.CharField(max_length=40, unique=True)
    hex_code = models.CharField(max_length=7, default="#000000", help_text="e.g. #FF0000")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    class Gender(models.TextChoices):
        MEN = "MEN", "Men"
        WOMEN = "WOMEN", "Women"
        BOYS = "BOYS", "Boys"
        GIRLS = "GIRLS", "Girls"
        KIDS = "KIDS", "Kids"
        UNISEX = "UNISEX", "Unisex"

    sku = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.UNISEX)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    fabric = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost price per unit (₹)")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base selling price (₹)")
    mrp = models.DecimalField(max_digits=10, decimal_places=2, help_text="MRP (₹)")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5,
                                       help_text="Applicable GST % (e.g. 5, 12, 18)")
    minimum_stock = models.PositiveIntegerField(default=5)
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_added"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse("storefront:product_detail", args=[self.slug])

    @property
    def total_stock(self):
        return sum(v.stock_quantity for v in self.variants.all())

    @property
    def is_low_stock(self):
        return 0 < self.total_stock <= self.minimum_stock

    @property
    def is_out_of_stock(self):
        return self.total_stock <= 0

    @property
    def effective_price(self):
        if self.discount_percent:
            return round(self.selling_price * (1 - self.discount_percent / 100), 2)
        return self.selling_price


class ProductVariant(models.Model):
    """A specific size+color combination of a product, each with its own stock/SKU/barcode."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.ForeignKey(Size, on_delete=models.PROTECT, related_name="variants")
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="variants")
    sku = models.CharField(max_length=50, unique=True, blank=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True)
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ("product", "size", "color")
        ordering = ["product", "size__display_order", "color__name"]

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.sku}-{self.size.label}-{self.color.name}".upper().replace(" ", "")
        if not self.barcode:
            import random
            self.barcode = f"8{self.product.id or 0:05d}{self.size.id or 0:02d}{self.color.id or 0:02d}{random.randint(100,999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.size.label} - {self.color.name}"

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.product.minimum_stock
