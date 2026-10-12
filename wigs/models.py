import math
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class StoreSettings(models.Model):
    store_name = models.CharField(max_length=100, default="Blessed Wigs")
    tagline = models.CharField(max_length=200, default="Luxury Handcrafted Wigs & Raw Virgin Hair")
    announcement_bar = models.CharField(
        max_length=250, 
        default="✨ Exclusive 6% discount automatically applied on all luxury wigs this week! Fast Nationwide & Worldwide Delivery ✨"
    )
    phone_number = models.CharField(max_length=30, default="+234 812 345 6789")
    whatsapp_number = models.CharField(max_length=30, default="+2348123456789")
    admin_email = models.EmailField(default="orders@blessedwigs.com")
    currency_symbol = models.CharField(max_length=10, default="₦")
    
    # 2 Bank Details as requested
    bank_1_name = models.CharField(max_length=100, default="Guaranty Trust Bank (GTBank)")
    bank_1_account_number = models.CharField(max_length=20, default="0123456789")
    bank_1_account_name = models.CharField(max_length=150, default="Blessed Wigs Luxury Brand")

    bank_2_name = models.CharField(max_length=100, default="Zenith Bank")
    bank_2_account_number = models.CharField(max_length=20, default="2098765432")
    bank_2_account_name = models.CharField(max_length=150, default="Blessed Wigs Enterprises")

    class Meta:
        verbose_name = "Store & Bank Settings"
        verbose_name_plural = "Store & Bank Settings"

    def __str__(self):
        return f"{self.store_name} Configuration"

    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(id=1)
        return settings


class Wig(models.Model):
    name = models.CharField(max_length=200, help_text="e.g. Raw Bone Straight Luxe Frontal")
    product_id = models.CharField(max_length=50, unique=True, help_text="Unique Product ID e.g. BW-101")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    
    original_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Original price before discount")
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('6.00'), 
        help_text="Standard discount percentage (defaults to 6%)"
    )
    
    stock = models.PositiveIntegerField(default=3, help_text="Number of this particular wig left in stock")
    color = models.CharField(max_length=100, default="Natural Black 1B", help_text="e.g. 99J Burgundy, Honey Blonde, Natural Black")
    make = models.CharField(max_length=255, default="13x4 HD Lace Frontal, 250% Density", help_text="e.g. HD Swiss Lace, Full Lace, Glueless Closure")
    length_inches = models.PositiveIntegerField(default=24, help_text="Length in inches (e.g. 24)")
    texture = models.CharField(max_length=100, default="Bone Straight", help_text="e.g. Bone Straight, Body Wave, Deep Wave")
    description = models.TextField(help_text="Detailed description, hair origin, and styling tips")
    
    main_image = models.ImageField(upload_to='wigs/images/', help_text="Main high-definition wig photo")
    video_file = models.FileField(upload_to='wigs/videos/', blank=True, null=True, help_text="Optional uploaded MP4 video")
    video_url = models.URLField(blank=True, null=True, help_text="Direct link or embed to video / Instagram reel / TikTok")
    
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.product_id})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.product_id}")
        super().save(*args, **kwargs)

    @property
    def discount_price(self):
        """Calculates price with 6% discount"""
        factor = Decimal('1.00') - (self.discount_percentage / Decimal('100.00'))
        return round(self.original_price * factor, 2)

    @property
    def savings_amount(self):
        """Calculates amount saved with 6% discount"""
        return round(self.original_price - self.discount_price, 2)

    @property
    def is_in_stock(self):
        return self.stock > 0

    def get_absolute_url(self):
        return reverse('wigs:detail', kwargs={'slug': self.slug})


class WigImage(models.Model):
    wig = models.ForeignKey(Wig, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='wigs/gallery/')
    caption = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Gallery Image for {self.wig.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid & Payment Verified'),
        ('pending_verification', 'Awaiting Bank Transfer Check'),
        ('processing', 'Customizing / Processing'),
        ('shipped', 'Shipped / Dispatched'),
        ('delivered', 'Delivered to Customer'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    wig = models.ForeignKey(Wig, on_delete=models.SET_NULL, null=True, blank=True)
    product_id = models.CharField(max_length=50, help_text="Product ID of the wig")
    wig_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Customer Info & Shipping Address
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    delivery_notes = models.TextField(blank=True)
    
    # Payment verification
    bank_selected = models.CharField(max_length=150, default="Bank Transfer")
    payment_receipt = models.ImageField(upload_to='orders/receipts/', blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='paid')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name} ({self.product_id})"


class Inquiry(models.Model):
    """Key 2 = Ask (Questions about specific wig or customer service)"""
    STATUS_CHOICES = [
        ('new', 'New Question'),
        ('answered', 'Answered'),
        ('closed', 'Closed'),
    ]

    wig = models.ForeignKey(Wig, on_delete=models.SET_NULL, null=True, blank=True)
    product_id = models.CharField(max_length=50, blank=True)
    wig_name = models.CharField(max_length=200, blank=True)
    customer_name = models.CharField(max_length=120)
    customer_contact = models.CharField(max_length=100, help_text="Phone, WhatsApp or Email")
    message = models.TextField()
    admin_response = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Customer Inquiries (Ask)"

    def __str__(self):
        return f"Inquiry from {self.customer_name} regarding {self.product_id or 'General'}"


class RefundRequest(models.Model):
    """Refund option for paid products"""
    STATUS_CHOICES = [
        ('requested', 'Refund Requested'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved & Refund Issued'),
        ('rejected', 'Rejected'),
    ]

    order_number = models.CharField(max_length=50)
    product_id = models.CharField(max_length=50, help_text="Product ID of the wig")
    wig_name = models.CharField(max_length=200, blank=True)
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    
    # Refund bank details
    bank_name = models.CharField(max_length=100, help_text="Customer Bank for Refund")
    account_number = models.CharField(max_length=30, help_text="Customer Account Number")
    account_name = models.CharField(max_length=150, help_text="Customer Account Name")
    
    reason = models.TextField()
    proof_image = models.ImageField(upload_to='refunds/proofs/', blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='requested')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund #{self.id} for Product {self.product_id} ({self.customer_name})"


class AdminAlert(models.Model):
    """Alerts automatically dispatched to sister/admin"""
    ALERT_TYPES = [
        ('payment', 'Product Paid For'),
        ('refund', 'Refund Requested'),
        ('inquiry', 'Customer Question'),
    ]

    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    product_id = models.CharField(max_length=50, blank=True)
    order_number = models.CharField(max_length=50, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.alert_type.upper()}] {self.title} - {self.product_id}"
