from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test bulk order email functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing bulk order email functionality...')
        
        # Test admin notification email
        admin_subject = "BULK/CUSTOM ORDER REQUEST - Test Product"
        
        admin_body = """
ADMIN NOTIFICATION - BULK/CUSTOM ORDER REQUEST

A buyer has submitted a Bulk Order request that requires your attention.

BUYER DETAILS:
- Name: Test Buyer
- Email: test@example.com
- Message Type: Bulk Order

PRODUCT DETAILS:
- Product: Test Product
- Seller: Test Seller (seller@example.com)
- Current Price: ₱100.00
- Product URL: http://example.com/product/test

ORDER DETAILS:
- Quantity Requested: 50
- Preferred Delivery Date: 2024-01-15
- Special Requirements: Custom packaging required

BUYER MESSAGE:
Subject: Bulk Order Request
Message: I need 50 units of this product for my business. Please let me know about bulk pricing and delivery options.

ACTION REQUIRED:
1. Review the request details
2. Contact the seller via hardcopy paper
3. Coordinate between buyer and seller
4. Update order status in the system

This request has been automatically sent to you for processing.
Please handle this request promptly and ensure proper communication between all parties.

Best regards,
Local Marketplace System
        """
        
        try:
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@localmarketplace.com')
            send_mail(
                subject=admin_subject,
                message=admin_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('Admin notification email sent successfully!')
            )
            
            # Test buyer confirmation email
            buyer_subject = "Bulk Order Request Received - Test Product"
            buyer_body = """
Hello Test Buyer,

Thank you for your Bulk Order request for "Test Product".

Your request has been received and is being processed by our admin team.

REQUEST SUMMARY:
- Product: Test Product
- Quantity: 50
- Delivery Date: 2024-01-15
- Special Requirements: Custom packaging required

Your message: I need 50 units of this product for my business. Please let me know about bulk pricing and delivery options.

NEXT STEPS:
1. Our admin team will review your request
2. They will contact the seller on your behalf
3. You will receive updates via email
4. The admin will coordinate the order process

Please note that bulk and custom orders require additional processing time.
We will contact you soon with further details.

If you have any urgent questions, please contact our support team.

Best regards,
Local Marketplace Admin Team
            """
            
            send_mail(
                subject=buyer_subject,
                message=buyer_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@example.com'],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('Buyer confirmation email sent successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send emails: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('Make sure to configure your email settings in settings.py')
            ) 