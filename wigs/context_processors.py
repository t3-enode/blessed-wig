from .models import StoreSettings

def store_context(request):
    """Provides global store settings and cart summary to every template"""
    settings = StoreSettings.get_settings()
    
    # Retrieve cart from session
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 1) for item in cart.values())
    
    return {
        'store_settings': settings,
        'cart_count': cart_count,
    }
