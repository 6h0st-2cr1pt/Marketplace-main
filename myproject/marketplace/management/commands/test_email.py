from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing email functionality...')
        
        try:
            send_mail(
                subject='Test Email from Local Marketplace',
                message='This is a test email to verify that the email functionality is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@example.com'],  # Replace with your test email
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('Email sent successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('Make sure to configure your email settings in settings.py')
            ) 