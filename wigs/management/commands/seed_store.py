import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io

from wigs.models import StoreSettings, Wig, Order, Inquiry, AdminAlert

User = get_user_model()

def generate_wig_placeholder_image(name, color_name, bg_hex="#6B1D2F"):
    """Generate high-quality aesthetic placeholder image for wig"""
    img = Image.new('RGB', (800, 1000), color=bg_hex)
    draw = ImageDraw.Draw(img)
    
    # Draw artistic decorative borders
    draw.rectangle([30, 30, 770, 970], outline="#FAF7F2", width=3)
    draw.rectangle([45, 45, 755, 955], outline="#F5C2B8", width=1)
    
    # Draw luxury text
    draw.text((400, 420), "BLESSED WIGS", fill="#FAF7F2", anchor="mm")
    draw.text((400, 470), "• LUXURY RAW HAIR •", fill="#F5C2B8", anchor="mm")
    draw.text((400, 530), name, fill="#FFFFFF", anchor="mm")
    draw.text((400, 580), f"Color: {color_name}", fill="#F5C2B8", anchor="mm")
    draw.text((400, 630), "6% PROMO DISCOUNT APPLIED", fill="#D9531E", anchor="mm")
    
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    return ContentFile(buffer.getvalue())

class Command(BaseCommand):
    help = 'Seeds initial store settings, admin user, and luxury wigs collection'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Blessed Wigs database...")

        # 1. Create or update Admin User
        admin_user, created = User.objects.get_or_create(username='admin')
        admin_user.set_password('blessedwigs2026!')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.email = 'admin@blessedwigs.com'
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("Admin user ready: admin / blessedwigs2026!"))

        # 2. Store & Bank Settings (The 2 official bank accounts)
        settings = StoreSettings.get_settings()
        settings.store_name = "Blessed Wigs"
        settings.tagline = "Handcrafted Luxury Wigs, HD Lace & 100% Raw Virgin Hair"
        settings.phone_number = "+234 812 345 6789"
        settings.whatsapp_number = "+2348123456789"
        settings.admin_email = "orders@blessedwigs.com"
        settings.currency_symbol = "₦"
        
        # Bank 1
        settings.bank_1_name = "Guaranty Trust Bank (GTBank)"
        settings.bank_1_account_number = "0123456789"
        settings.bank_1_account_name = "Blessed Wigs Luxury Brand"
        
        # Bank 2
        settings.bank_2_name = "Zenith Bank"
        settings.bank_2_account_number = "2098765432"
        settings.bank_2_account_name = "Blessed Wigs Global Ventures"
        
        settings.save()
        self.stdout.write(self.style.SUCCESS("Store and 2 bank accounts initialized."))

        # 3. Sample Luxury Wigs
        sample_wigs_data = [
            {
                'name': 'Raw Bone Straight HD Frontal',
                'product_id': 'BW-101',
                'original_price': Decimal('135000.00'),
                'stock': 4,
                'color': 'Natural Black 1B',
                'make': '13x4 HD Invisible Swiss Lace, 250% Density',
                'length_inches': 26,
                'texture': 'Bone Straight',
                'description': 'Unprocessed raw single-donor hair with silky cuticle alignment from root to tip. Tangle-free, bleaches up to 613 platinum blonde with zero shedding. Pre-plucked hairline with ultra-thin HD lace that blends effortlessly into any skin tone.',
                'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
                'bg_hex': '#4A0E17',
                'is_featured': True,
            },
            {
                'name': 'Burgundy Wine Luxury Body Wave',
                'product_id': 'BW-102',
                'original_price': Decimal('148000.00'),
                'stock': 2,
                'color': '99J Burgundy / Deep Wine',
                'make': '13x6 Deep Part HD Lace, 220% Density',
                'length_inches': 24,
                'texture': 'Body Wave',
                'description': 'Rich editorial burgundy wine tone custom-dyed on raw virgin hair. Luscious, bouncy waves that hold curls for days. Pre-bleached knots and customized glueless elastic band included for seamless wear.',
                'video_url': '',
                'bg_hex': '#6B1D2F',
                'is_featured': True,
            },
            {
                'name': 'Honey Blonde Piano Highlight Frontal',
                'product_id': 'BW-103',
                'original_price': Decimal('165000.00'),
                'stock': 3,
                'color': 'Piano Highlight #4/#27',
                'make': 'Full Frontal 13x4 HD Lace, 250% Density',
                'length_inches': 22,
                'texture': 'Silky Straight',
                'description': 'Stunning multi-dimensional honey blonde and warm caramel ribbons on dark chocolate base. Pre-plucked natural hairline with baby hairs. Super soft texture that flows in the wind.',
                'video_url': '',
                'bg_hex': '#7A3816',
                'is_featured': True,
            },
            {
                'name': 'Bohemian Deep Curly Goddess Unit',
                'product_id': 'BW-104',
                'original_price': Decimal('178000.00'),
                'stock': 1,
                'color': 'Natural Dark Brown #2',
                'make': '5x5 HD Glueless Closure, 280% High Density',
                'length_inches': 28,
                'texture': 'Deep Curly',
                'description': 'Juicy, hydrated spiral curls that define effortlessly with water and leave-in conditioner. No matting, no tangling. Completely glueless with adjustable security straps.',
                'video_url': '',
                'bg_hex': '#2C1B18',
                'is_featured': True,
            },
            {
                'name': 'Blunt Cut Sleek Parisian Bob',
                'product_id': 'BW-105',
                'original_price': Decimal('98000.00'),
                'stock': 5,
                'color': 'Jet Black #1',
                'make': '4x4 HD Lace Closure, 180% Density',
                'length_inches': 14,
                'texture': 'Bone Straight',
                'description': 'Chic, razor-sharp blunt bob cut tailored for a sophisticated look. Lightweight, breathable cap with premium HD lace closure.',
                'video_url': '',
                'bg_hex': '#1A1A1A',
                'is_featured': False,
            },
        ]

        for wig_info in sample_wigs_data:
            bg_hex = wig_info.pop('bg_hex')
            wig, created = Wig.objects.get_or_create(
                product_id=wig_info['product_id'],
                defaults=wig_info
            )
            if created or not wig.main_image:
                img_content = generate_wig_placeholder_image(wig.name, wig.color, bg_hex)
                wig.main_image.save(f"{wig.product_id}.jpg", img_content, save=True)
                self.stdout.write(f"Created wig: {wig.name} ({wig.product_id}) with 6% auto-discount price: NGN {wig.discount_price:,.2f}")

        # 4. Create sample initial alert so Sister's Dashboard is lively
        if not AdminAlert.objects.exists():
            AdminAlert.objects.create(
                alert_type='payment',
                title='System Ready: Blessed Wigs Platform Live',
                message='Welcome to Blessed Wigs! The web app is connected and monitoring all wig sales and refunds.',
                product_id='BW-101'
            )

        self.stdout.write(self.style.SUCCESS("All sample data seeded successfully!"))
