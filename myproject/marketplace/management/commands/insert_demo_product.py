from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from marketplace.models import Category, Region, City, Product, ProductImage

class Command(BaseCommand):
    help = 'Insert a demo product with image_url for a local Philippine product.'

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username='demo_seller',
            defaults={'email': 'demo_seller@example.com'}
        )
        if not user.has_usable_password():
            user.set_password('demo12345')
            user.save()

        category, _ = Category.objects.get_or_create(
            name='Natural Cosmetics',
            defaults={'slug': 'natural-cosmetics', 'description': 'Natural and organic beauty products.', 'unit': 'piece'}
        )
        region = Region.objects.get(name='luzon')
        city = City.objects.get(name='Manila', region=region)
        product, created = Product.objects.get_or_create(
            seller=user,
            name='Philippine Coconut Oil',
            slug='philippine-coconut-oil',
            defaults={
                'description': 'Pure, cold-pressed coconut oil from the Philippines.',
                'price': 250.00,
                'stock': 100,
                'category': category,
                'location': 'Manila',
                'region': region,
                'city': city,
                'is_active': True
            }
        )
        image_url = 'https://images.unsplash.com/photo-1504674900247-0877df9cc836'
        ProductImage.objects.get_or_create(
            product=product,
            image_url=image_url,
            defaults={'is_primary': True}
        )
        self.stdout.write(self.style.SUCCESS('Demo product and image created successfully.')) 