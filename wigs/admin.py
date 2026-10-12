from django.contrib import admin
from django.utils.html import format_html
from .models import StoreSettings, Wig, WigImage, Order, Inquiry, RefundRequest, AdminAlert


class WigImageInline(admin.TabularInline):
    model = WigImage
    extra = 2
    fields = ('image', 'caption')


@admin.register(Wig)
class WigAdmin(admin.ModelAdmin):
    list_display = ('image_thumbnail', 'name', 'product_id', 'formatted_price', 'formatted_discount_price', 'stock_badge', 'color', 'length_inches', 'is_featured', 'is_active')
    list_filter = ('is_active', 'is_featured', 'color', 'texture')
    search_fields = ('name', 'product_id', 'color', 'description')
    prepopulated_fields = {'slug': ('name', 'product_id')}
    inlines = [WigImageInline]
    readonly_fields = ('image_preview', 'calculated_discount_display')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'product_id', 'slug', 'is_active', 'is_featured')
        }),
        ('Pricing & Automatic 6% Discount', {
            'fields': ('original_price', 'discount_percentage', 'calculated_discount_display'),
            'description': 'The system automatically applies your 6% discount and shows it to customers.'
        }),
        ('Inventory & Specifications', {
            'fields': ('stock', 'color', 'make', 'length_inches', 'texture', 'description')
        }),
        ('Media (Photo & Video)', {
            'fields': ('main_image', 'image_preview', 'video_file', 'video_url'),
            'description': 'Upload high-res photos and video showing hair movement, bounce, and lace perfection.'
        }),
    )

    def image_thumbnail(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />', obj.main_image.url)
        return "No Photo"
    image_thumbnail.short_description = "Photo"

    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 250px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />', obj.main_image.url)
        return "Upload photo to preview"
    image_preview.short_description = "Main Photo Preview"

    def formatted_price(self, obj):
        return f"₦{obj.original_price:,.2f}"
    formatted_price.short_description = "Original Price"

    def formatted_discount_price(self, obj):
        return format_html(
            '<span style="color: #6B1D2F; font-weight: bold;">₦{:,.2f}</span> <small style="color: #D9531E;">(-{}%)</small>',
            obj.discount_price, obj.discount_percentage
        )
    formatted_discount_price.short_description = "Discount Price (6%)"

    def calculated_discount_display(self, obj):
        if obj.original_price:
            return format_html(
                '<div style="background: #FDF9F3; padding: 10px; border-left: 4px solid #D9531E; border-radius: 4px;">'
                '<strong>Customer Price:</strong> ₦{:,.2f}<br>'
                '<strong>Savings for Customer:</strong> ₦{:,.2f} ({}% OFF)'
                '</div>',
                obj.discount_price, obj.savings_amount, obj.discount_percentage
            )
        return "Save to compute discount"
    calculated_discount_display.short_description = "Auto-Calculated Discount"

    def stock_badge(self, obj):
        if obj.stock <= 0:
            return format_html('<span style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">Sold Out</span>')
        elif obj.stock <= 2:
            return format_html('<span style="background: #ffc107; color: #212529; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">Low: {} left</span>', obj.stock)
        return format_html('<span style="background: #198754; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{} in stock</span>', obj.stock)
    stock_badge.short_description = "Stock Left"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'product_id', 'wig_name', 'customer_name', 'customer_phone', 'formatted_total', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'product_id', 'customer_name', 'customer_phone', 'customer_email')
    readonly_fields = ('order_number', 'product_id', 'wig_name', 'total_price', 'receipt_preview', 'created_at')
    
    fieldsets = (
        ('Order & Product Details', {
            'fields': ('order_number', 'product_id', 'wig', 'wig_name', 'quantity', 'unit_price', 'total_price', 'status')
        }),
        ('Customer & Delivery Address', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'shipping_address', 'city', 'state', 'delivery_notes')
        }),
        ('Payment Verification', {
            'fields': ('bank_selected', 'payment_receipt', 'receipt_preview')
        }),
    )

    def formatted_total(self, obj):
        return f"₦{obj.total_price:,.2f}"
    formatted_total.short_description = "Total Paid"

    def receipt_preview(self, obj):
        if obj.payment_receipt:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 250px; border-radius: 8px; border: 1px solid #ccc;" /><br>View Full Proof</a>',
                obj.payment_receipt.url, obj.payment_receipt.url
            )
        return "No receipt uploaded"
    receipt_preview.short_description = "Transfer Proof"

    def status_badge(self, obj):
        colors = {
            'paid': '#198754',
            'pending_verification': '#ffc107',
            'processing': '#0d6efd',
            'shipped': '#6f42c1',
            'delivered': '#20c997',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        text_color = '#000' if obj.status == 'pending_verification' else '#fff'
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, text_color, obj.get_status_display()
        )
    status_badge.short_description = "Status"


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_contact', 'product_id', 'wig_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_contact', 'product_id', 'message')
    readonly_fields = ('product_id', 'wig_name', 'created_at')


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'order_number', 'customer_name', 'customer_phone', 'bank_name', 'account_number', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product_id', 'order_number', 'customer_name', 'customer_phone', 'account_number')
    readonly_fields = ('proof_preview', 'created_at')

    def proof_preview(self, obj):
        if obj.proof_image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 200px; border-radius: 6px;" /><br>View Attachment</a>',
                obj.proof_image.url, obj.proof_image.url
            )
        return "No image attached"
    proof_preview.short_description = "Refund Proof / Item Photo"

    def status_badge(self, obj):
        colors = {
            'requested': '#fd7e14',
            'under_review': '#0dcaf0',
            'approved': '#198754',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Refund Status"


@admin.register(AdminAlert)
class AdminAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'product_id', 'order_number', 'is_read', 'created_at')
    list_filter = ('alert_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'product_id', 'order_number')


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Store Identity', {
            'fields': ('store_name', 'tagline', 'announcement_bar', 'currency_symbol')
        }),
        ('Contact Channels', {
            'fields': ('phone_number', 'whatsapp_number', 'admin_email')
        }),
        ('Official Bank Account #1 (Displayed at Checkout)', {
            'fields': ('bank_1_name', 'bank_1_account_number', 'bank_1_account_name')
        }),
        ('Official Bank Account #2 (Displayed at Checkout)', {
            'fields': ('bank_2_name', 'bank_2_account_number', 'bank_2_account_name')
        }),
    )

    def has_add_permission(self, request):
        # Only allow 1 settings record
        return not StoreSettings.objects.exists()
