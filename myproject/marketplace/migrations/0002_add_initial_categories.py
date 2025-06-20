from django.db import migrations
from django.utils.text import slugify

def add_initial_categories(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    
    categories = [
        {
            'name': 'Handicrafts',
            'description': 'Unique handmade items crafted with care and creativity.',
            'unit': 'piece'
        },
        {
            'name': 'Fresh Fruits',
            'description': 'Fresh and seasonal fruits from local farmers.',
            'unit': 'kg'
        },
        {
            'name': 'Fresh Vegetables',
            'description': 'Fresh and organic vegetables from local farms.',
            'unit': 'kg'
        },
        {
            'name': 'Art & Design',
            'description': 'Original artwork, prints, and design pieces.',
            'unit': 'piece'
        },
        {
            'name': 'Organic Products',
            'description': 'Natural and organic products for a healthier lifestyle.',
            'unit': 'piece'
        },
        {
            'name': 'Local Services',
            'description': 'Services offered by local artisans and professionals.',
            'unit': 'piece'
        },
        {
            'name': 'Home Decor',
            'description': 'Beautiful items to enhance your living space.',
            'unit': 'piece'
        },
        {
            'name': 'Bakery',
            'description': 'Freshly baked goods and pastries.',
            'unit': 'piece'
        },
        {
            'name': 'Dairy Products',
            'description': 'Fresh dairy products from local farms.',
            'unit': 'piece'
        },
        {
            'name': 'Handmade Crafts',
            'description': 'Unique handmade crafts and artisanal products.',
            'unit': 'piece'
        },
        {
            'name': 'Natural Cosmetics',
            'description': 'Natural and organic beauty products.',
            'unit': 'piece'
        },
        {
            'name': 'Preserves & Jams',
            'description': 'Homemade preserves, jams, and pickles.',
            'unit': 'piece'
        },
        {
            'name': 'Textiles',
            'description': 'Handwoven and handcrafted textile products.',
            'unit': 'piece'
        },
        {
            'name': 'Woodwork',
            'description': 'Handcrafted wooden furniture and decor items.',
            'unit': 'piece'
        }
    ]
    
    for category_data in categories:
        slug = slugify(category_data['name'])
        Category.objects.get_or_create(
            slug=slug,
            defaults={
                'name': category_data['name'],
                'description': category_data['description'],
                'unit': category_data['unit']
            }
        )

def remove_initial_categories(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_categories, remove_initial_categories),
    ] 