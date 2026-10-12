import json
import uuid
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Wig, StoreSettings, Order, Inquiry, RefundRequest, AdminAlert


def index(request):
    """
    Main storefront with artistic luxury palette:
    Burgundy, Burnt Orange, Milk, Black, Silk Pink, and White background.
    Supports direct deep-links from Instagram / ads via ?wig=PRODUCT_ID_OR_SLUG
    """
    wigs = Wig.objects.filter(is_active=True).prefetch_related('gallery_images')
    settings_obj = StoreSettings.get_settings()
    
    # Query filters
    query = request.GET.get('q', '').strip()
    texture_filter = request.GET.get('texture', '').strip()
    color_filter = request.GET.get('color', '').strip()
    
    if query:
        wigs = wigs.filter(name__icontains=query) | wigs.filter(description__icontains=query) | wigs.filter(product_id__icontains=query)
    if texture_filter:
        wigs = wigs.filter(texture__iexact=texture_filter)
    if color_filter:
        wigs = wigs.filter(color__iexact=color_filter)

    # Deep-link support from Instagram / Social Media (e.g. ?wig=BW-101 or ?wig=slug)
    targeted_wig = None
    target_param = request.GET.get('wig')
    if target_param:
        targeted_wig = (
            wigs.filter(product_id__iexact=target_param).first() or 
            wigs.filter(slug__iexact=target_param).first()
        )

    # Collect unique textures and colors for filter badges
    all_textures = Wig.objects.filter(is_active=True).values_list('texture', flat=True).distinct()
    all_colors = Wig.objects.filter(is_active=True).values_list('color', flat=True).distinct()

    context = {
        'wigs': wigs,
        'targeted_wig': targeted_wig,
        'all_textures': all_textures,
        'all_colors': all_colors,
        'selected_texture': texture_filter,
        'selected_color': color_filter,
        'search_query': query,
    }
    return render(request, 'wigs/index.html', context)


def wig_detail(request, slug):
    """Dedicated landing page for a specific wig â€” ideal for Instagram bio and ads"""
    wig = get_object_or_404(Wig, slug=slug, is_active=True)
    related_wigs = Wig.objects.filter(is_active=True).exclude(id=wig.id)[:4]
    
    return render(request, 'wigs/detail.html', {
        'wig': wig,
        'related_wigs': related_wigs,
    })


def buy_now(request, product_id):
    """
    Key 1 = Buy (Green Button): Direct checkout screen with:
    - 2 official bank accounts details
    - Customer shipping address form
    - Proof of payment / receipt upload
    - Auto-notifies admin: 'This product has been paid for' with Product ID
    """
    wig = get_object_or_404(Wig, product_id=product_id, is_active=True)
    store_settings = StoreSettings.get_settings()

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        delivery_notes = request.POST.get('delivery_notes', '').strip()
        bank_selected = request.POST.get('bank_selected', 'Bank 1')
        quantity = int(request.POST.get('quantity', 1))
        
        # Calculate totals
        unit_price = wig.discount_price
        total_price = unit_price * quantity
        
        # Unique Order Number
        order_number = f"ORD-{uuid.uuid4().hex[:7].upper()}"

        receipt_file = request.FILES.get('payment_receipt')

        # Create Order
        order = Order.objects.create(
            order_number=order_number,
            wig=wig,
            product_id=wig.product_id,
            wig_name=wig.name,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            city=city,
            state=state,
            delivery_notes=delivery_notes,
            bank_selected=bank_selected,
            payment_receipt=receipt_file,
            status='paid' if receipt_file else 'pending_verification'
        )

        # Decrement stock if stock > 0
        if wig.stock >= quantity:
            wig.stock -= quantity
            wig.save(update_fields=['stock'])

        # Send alert to Admin as specified: "this product has been paid for" with product id
        admin_message = (
            f"This product has been paid for!\n\n"
            f"Product ID: #{wig.product_id}\n"
            f"Wig Name: {wig.name}\n"
            f"Order Number: #{order.order_number}\n"
            f"Amount Paid: â‚¦{total_price:,.2f} (Includes 6% discount)\n"
            f"Customer Name: {customer_name}\n"
            f"Customer Phone: {customer_phone}\n"
            f"Shipping To: {shipping_address}, {city}, {state}\n"
            f"Bank Transferred To: {bank_selected}"
        )

        AdminAlert.objects.create(
            alert_type='payment',
            title=f"This product has been paid for: {wig.product_id}",
            message=admin_message,
            product_id=wig.product_id,
            order_number=order.order_number
        )

        # Also trigger console/email notification
        try:
            send_mail(
                subject=f"[BLESSED WIGS ORDER] This product has been paid for: #{wig.product_id}",
                message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'orders@blessedwigs.com',
                recipient_list=[store_settings.admin_email],
                fail_silently=True
            )
        except Exception:
            pass

        return redirect('wigs:order_success', order_number=order.order_number)

    return render(request, 'wigs/buy_now.html', {
        'wig': wig,
        'store_settings': store_settings,
    })


def order_success(request, order_number):
    """Customer order confirmation screen"""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'wigs/order_success.html', {
        'order': order,
    })


@require_POST
def submit_inquiry(request):
    """
    Key 2 = Ask (Orange Button):
    Customer submits an inquiry regarding a wig or customization.
    """
    product_id = request.POST.get('product_id', '').strip()
    customer_name = request.POST.get('customer_name', '').strip()
    customer_contact = request.POST.get('customer_contact', '').strip()
    message = request.POST.get('message', '').strip()

    wig = None
    wig_name = ""
    if product_id:
        wig = Wig.objects.filter(product_id=product_id).first()
        if wig:
            wig_name = wig.name

    inquiry = Inquiry.objects.create(
        wig=wig,
        product_id=product_id,
        wig_name=wig_name,
        customer_name=customer_name,
        customer_contact=customer_contact,
        message=message
    )

    # Dispatched Admin Alert
    AdminAlert.objects.create(
        alert_type='inquiry',
        title=f"New Question on Product ID: #{product_id or 'General'}",
        message=f"Customer: {customer_name} ({customer_contact})\nQuestion: {message}",
        product_id=product_id
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you, gorgeous! Your question has been delivered to the admin. We will reply via WhatsApp/call shortly.'
        })

    messages.success(request, 'Thank you! Your question has been sent to our styling specialist.')
    return redirect(request.META.get('HTTP_REFERER', 'wigs:index'))


def refund_request_view(request):
    """
    Refund screen:
    - Customer submits refund for a paid product
    - Sends product ID and refund details to Admin
    """
    initial_product_id = request.GET.get('product_id', '')
    initial_order_number = request.GET.get('order_number', '')

    if request.method == 'POST':
        order_number = request.POST.get('order_number', '').strip()
        product_id = request.POST.get('product_id', '').strip()
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        account_name = request.POST.get('account_name', '').strip()
        reason = request.POST.get('reason', '').strip()
        proof_image = request.FILES.get('proof_image')

        # Find wig details
        wig_name = ""
        wig = Wig.objects.filter(product_id=product_id).first()
        if wig:
            wig_name = wig.name

        # Create Refund Request
        refund = RefundRequest.objects.create(
            order_number=order_number,
            product_id=product_id,
            wig_name=wig_name,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            bank_name=bank_name,
            account_number=account_number,
            account_name=account_name,
            reason=reason,
            proof_image=proof_image
        )

        # Notify Admin: Send Product ID with refund notification
        admin_message = (
            f"Customer Refund Request Received!\n\n"
            f"Product ID: #{product_id}\n"
            f"Order Number: #{order_number}\n"
            f"Customer Name: {customer_name}\n"
            f"Customer Contact: {customer_phone} ({customer_email})\n"
            f"Customer Refund Account: {bank_name} - {account_number} ({account_name})\n"
            f"Reason: {reason}"
        )

        AdminAlert.objects.create(
            alert_type='refund',
            title=f"Refund Request for Product ID: #{product_id}",
            message=admin_message,
            product_id=product_id,
            order_number=order_number
        )

        try:
            settings_obj = StoreSettings.get_settings()
            send_mail(
                subject=f"[REFUND ALERT] Product ID #{product_id} Refund Requested",
                message=admin_message,
                from_email='orders@blessedwigs.com',
                recipient_list=[settings_obj.admin_email],
                fail_silently=True
            )
        except Exception:
            pass

        return render(request, 'wigs/refund_success.html', {
            'refund': refund,
        })

    return render(request, 'wigs/refund_form.html', {
        'initial_product_id': initial_product_id,
        'initial_order_number': initial_order_number,
    })


# Key 3 = Cart Views
def add_to_cart(request, product_id):
    """Key 3 = Cart: Add item to shopping cart"""
    wig = get_object_or_404(Wig, product_id=product_id, is_active=True)
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {
            'product_id': wig.product_id,
            'name': wig.name,
            'price': float(wig.discount_price),
            'original_price': float(wig.original_price),
            'image_url': wig.main_image.url if wig.main_image else '',
            'color': wig.color,
            'length': wig.length_inches,
            'quantity': 1,
        }
    
    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_items = sum(item['quantity'] for item in cart.values())
        return JsonResponse({
            'status': 'success',
            'cart_count': total_items,
            'message': f'{wig.name} added to your cart!'
        })

    messages.success(request, f'Added {wig.name} to your cart.')
    return redirect(request.META.get('HTTP_REFERER', 'wigs:index'))


def remove_from_cart(request, product_id):
    """Remove item from cart"""
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('wigs:cart_view')


def cart_view(request):
    """Cart drawer and page"""
    cart = request.session.get('cart', {})
    cart_items = list(cart.values())
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    original_total = sum(item['original_price'] * item['quantity'] for item in cart_items)
    total_savings = original_total - total_amount

    return render(request, 'wigs/cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'original_total': original_total,
        'total_savings': total_savings,
    })


def blessed_dashboard(request):
    """
    Mobile-friendly Blessed Quick Command Center:
    Allows your Blessed to view recent paid alerts, refund requests, and customer questions
    without logging into the complex backend admin.
    """
    alerts = AdminAlert.objects.all()[:20]
    recent_orders = Order.objects.all()[:10]
    recent_refunds = RefundRequest.objects.all()[:10]
    recent_inquiries = Inquiry.objects.all()[:10]
    store_settings = StoreSettings.get_settings()

    return render(request, 'wigs/blessed_dashboard.html', {
        'alerts': alerts,
        'recent_orders': recent_orders,
        'recent_refunds': recent_refunds,
        'recent_inquiries': recent_inquiries,
        'store_settings': store_settings,
    })

