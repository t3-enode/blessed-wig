from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from wigs.models import Wig, StoreSettings, Order, Inquiry, RefundRequest, AdminAlert

User = get_user_model()

class BlessedWigsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Setup Store & Bank Settings
        self.settings = StoreSettings.objects.create(
            store_name="Blessed Wigs",
            bank_1_name="GTBank",
            bank_1_account_number="0123456789",
            bank_1_account_name="Blessed Wigs Luxury",
            bank_2_name="Zenith Bank",
            bank_2_account_number="2098765432",
            bank_2_account_name="Blessed Wigs Ventures",
        )

        # Setup Sample Wig
        self.wig = Wig.objects.create(
            name="Raw Bone Straight Luxury Frontal",
            product_id="BW-101",
            original_price=Decimal("100000.00"),
            discount_percentage=Decimal("6.00"),
            stock=5,
            color="Natural Black 1B",
            make="13x4 HD Frontal",
            length_inches=26,
            texture="Bone Straight",
            description="100% Raw Virgin single donor hair."
        )

    def test_six_percent_discount_calculation(self):
        """Verify that 6% discount is automatically and accurately computed"""
        # Original: 100,000 -> 6% off should be 94,000
        self.assertEqual(self.wig.discount_price, Decimal("94000.00"))
        self.assertEqual(self.wig.savings_amount, Decimal("6000.00"))

    def test_homepage_loads_successfully(self):
        """Verify storefront homepage renders with status 200 and wig cards"""
        response = self.client.get(reverse('wigs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Blessed Wigs")
        self.assertContains(response, "BW-101")
        self.assertContains(response, "6% OFF")
        self.assertContains(response, "BUY")
        self.assertContains(response, "ASK")
        self.assertContains(response, "CART")

    def test_instagram_deep_link_highlight(self):
        """Verify visiting from Instagram ads with ?wig=BW-101 targets the wig"""
        response = self.client.get(reverse('wigs:index') + '?wig=BW-101')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['targeted_wig'], self.wig)

    def test_wig_detail_page(self):
        """Verify dedicated product page renders"""
        response = self.client.get(reverse('wigs:detail', kwargs={'slug': self.wig.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.wig.name)
        self.assertContains(response, "94000")

    def test_key1_buy_now_order_and_admin_alert(self):
        """
        Verify Key 1 (Buy) creates order, decrements stock, and alerts admin:
        'This product has been paid for' with Product ID
        """
        initial_stock = self.wig.stock
        payload = {
            'customer_name': 'Amara Kalu',
            'customer_email': 'amara@example.com',
            'customer_phone': '+2348011223344',
            'shipping_address': 'Plot 12 Admiralty Way, Lekki',
            'city': 'Lekki',
            'state': 'Lagos',
            'bank_selected': 'GTBank',
            'quantity': 1,
        }
        
        response = self.client.post(reverse('wigs:buy_now', kwargs={'product_id': self.wig.product_id}), payload)
        self.assertEqual(response.status_code, 302) # Redirect to success screen

        # Check stock decremented
        self.wig.refresh_from_db()
        self.assertEqual(self.wig.stock, initial_stock - 1)

        # Check Order created
        order = Order.objects.filter(product_id=self.wig.product_id).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, 'Amara Kalu')
        self.assertEqual(order.total_price, Decimal('94000.00'))

        # Check Admin Alert dispatched with 'This product has been paid for' and Product ID
        alert = AdminAlert.objects.filter(alert_type='payment', product_id=self.wig.product_id).first()
        self.assertIsNotNone(alert)
        self.assertIn("This product has been paid for", alert.title)
        self.assertIn(self.wig.product_id, alert.message)

    def test_key2_ask_inquiry(self):
        """Verify Key 2 (Ask) logs question and dispatches admin alert"""
        payload = {
            'product_id': self.wig.product_id,
            'customer_name': 'Zainab Bello',
            'customer_contact': '+2349098765432',
            'message': 'Can I request pre-bleached knots on this wig?'
        }
        response = self.client.post(reverse('wigs:ask_inquiry'), payload)
        self.assertEqual(response.status_code, 302)

        inquiry = Inquiry.objects.filter(customer_name='Zainab Bello').first()
        self.assertIsNotNone(inquiry)
        self.assertEqual(inquiry.product_id, self.wig.product_id)

        # Check Admin Alert
        alert = AdminAlert.objects.filter(alert_type='inquiry', product_id=self.wig.product_id).first()
        self.assertIsNotNone(alert)

    def test_key3_cart_flow(self):
        """Verify Key 3 (Cart) adds and updates session cart"""
        response = self.client.get(reverse('wigs:add_to_cart', kwargs={'product_id': self.wig.product_id}))
        self.assertEqual(response.status_code, 302)

        cart_response = self.client.get(reverse('wigs:cart_view'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, self.wig.name)
        self.assertContains(cart_response, "94000")

    def test_refund_request_dispatches_product_id_to_admin(self):
        """Verify customer refund request logs and notifies admin with Product ID"""
        payload = {
            'product_id': self.wig.product_id,
            'order_number': 'ORD-TEST123',
            'customer_name': 'Amara Kalu',
            'customer_email': 'amara@example.com',
            'customer_phone': '+2348011223344',
            'bank_name': 'Kuda Bank',
            'account_number': '1100223344',
            'account_name': 'Amara Kalu',
            'reason': 'Ordered wrong inch length by mistake, requesting exchange/reversal.'
        }

        response = self.client.post(reverse('wigs:refund_request'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Refund Request Logged")

        refund = RefundRequest.objects.filter(product_id=self.wig.product_id).first()
        self.assertIsNotNone(refund)
        self.assertEqual(refund.account_number, '1100223344')

        # Check Admin alert
        alert = AdminAlert.objects.filter(alert_type='refund', product_id=self.wig.product_id).first()
        self.assertIsNotNone(alert)
        self.assertIn(self.wig.product_id, alert.message)
