from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Region(models.Model):
    REGION_CHOICES = [
        ('luzon', 'Luzon'),
        ('visayas', 'Visayas'),
        ('mindanao', 'Mindanao'),
    ]
    
    name = models.CharField(max_length=50, choices=REGION_CHOICES, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('marketplace:region_detail', kwargs={'slug': self.slug})

class City(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Cities'
        ordering = ['name']
        unique_together = ['name', 'region']
    
    def __str__(self):
        return f"{self.name}, {self.region.get_name_display()}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('marketplace:city_detail', kwargs={'slug': self.slug})

class Category(models.Model):
    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Liter'),
        ('ml', 'Milliliter'),
        ('box', 'Box'),
        ('set', 'Set'),
        ('dozen', 'Dozen'),
        ('pack', 'Pack'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True, null=True, help_text="Paste an image URL to use a web image for this category.")
    is_primary = models.BooleanField(default=False, help_text="Mark this as the primary category image.")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_primary:
            Category.objects.exclude(pk=self.pk).update(is_primary=False)
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('marketplace:category', kwargs={'slug': self.slug})

class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=1, help_text="Number of items in stock")
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    location = models.CharField(max_length=100, help_text="Specific address or location details")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('marketplace:product_detail', kwargs={'slug': self.slug})

    def get_primary_image(self):
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image and getattr(primary_image.image, 'name', None):
            try:
                if primary_image.image and hasattr(primary_image.image, 'url'):
                    _ = primary_image.image.url  # Will raise ValueError if no file
                    return primary_image.image
            except Exception:
                pass
        # If no primary image is set or file is missing, return the first valid image
        for img in self.images.all():
            try:
                if img.image and hasattr(img.image, 'url'):
                    _ = img.image.url
                    return img.image
            except Exception:
                continue
        return None

    def is_in_stock(self):
        return self.stock > 0

    def can_add_to_cart(self, quantity=1):
        """Check if the specified quantity can be added to cart"""
        return self.stock >= quantity

    def get_stock_status(self):
        if self.stock <= 0:
            return "Out of Stock"
        elif self.stock <= 5:
            return f"Only {self.stock} left"
        else:
            return f"In Stock ({self.stock} available)"

    def get_average_rating(self):
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0

    def get_review_count(self):
        return self.reviews.count()

    def get_location_display(self):
        """Get formatted location display"""
        if self.city and self.region:
            return f"{self.city.name}, {self.region.get_name_display()}"
        elif self.region:
            return self.region.get_name_display()
        else:
            return self.location

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    image_url = models.URLField(blank=True, null=True, help_text="Paste an image URL to fetch from the web.")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other images of this product to not primary
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.quantity > self.product.stock:
            raise ValueError(f"Not enough stock available. Only {self.product.stock} items left for {self.product.name}.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_cost(self):
        return self.product.price * self.quantity

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.product.name}"

class Order(models.Model):
    PAYMENT_METHODS = [
        ('cod', 'Cash on Delivery'),
        ('credit_card', 'Credit Card'),
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
        ('paypal', 'PayPal'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.first_name and self.user:
            self.first_name = self.user.first_name
        if not self.last_name and self.user:
            self.last_name = self.user.last_name
        # If status is being changed to delivered and delivered_at is not set
        if self.status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_cost(self):
        return self.price * self.quantity

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user') # One review per user per product
        ordering = ['-created_at']
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f'{self.rating} stars for {self.product.name} by {self.user.username}'

class SellerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_profile')
    profile_pic = models.ImageField(upload_to='seller_profiles/', blank=True, null=True)
    name = models.CharField(max_length=150)
    address = models.TextField()

    def __str__(self):
        return self.name or self.user.username

def is_seller(self):
    return hasattr(self, 'seller_profile')

User.add_to_class('is_seller', property(is_seller))
