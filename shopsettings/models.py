from django.db import models


class ShopSettings(models.Model):
    """Singleton model holding shop-wide configuration."""

    shop_name = models.CharField(max_length=120, default="SRI KRISHNA")
    tagline = models.CharField(max_length=200, default="Fashion for Every Generation")
    logo = models.ImageField(upload_to="shop/", blank=True, null=True)
    address = models.TextField(default="Main Bazaar Road, Narasapur, Andhra Pradesh")
    landmark = models.CharField(max_length=150, blank=True, default="Near Bus Stand")
    phone = models.CharField(max_length=15, default="9876543210")
    whatsapp = models.CharField(max_length=15, default="9876543210")
    email = models.EmailField(blank=True, default="contact@srikrishnaclothing.in")
    gstin = models.CharField(max_length=20, blank=True, default="37ABCDE1234F1Z5")
    upi_id = models.CharField(max_length=60, blank=True, default="srikrishna@upi")
    invoice_prefix = models.CharField(max_length=10, default="SK")
    currency_symbol = models.CharField(max_length=5, default="₹")
    default_gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    business_hours = models.CharField(max_length=150, default="Mon - Sun: 9:30 AM - 9:30 PM")
    google_maps_embed_url = models.URLField(blank=True, default="")
    loyalty_points_per_100_rupees = models.PositiveIntegerField(default=2)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    last_backup_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Shop Settings"
        verbose_name_plural = "Shop Settings"

    def __str__(self):
        return self.shop_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
