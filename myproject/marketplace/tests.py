from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Product, Category, Cart, CartItem

class StockValidationTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test product with limited stock
        self.product = Product.objects.create(
            seller=self.user,
            name='Test Product',
            slug='test-product',
            description='Test product description',
            price=10.00,
            stock=5,
            category=self.category,
            location='Test Location'
        )
        
        # Create cart for user
        self.cart = Cart.objects.create(user=self.user)

    def test_product_stock_validation(self):
        """Test that product stock validation works correctly"""
        # Test valid quantity
        self.assertTrue(self.product.can_add_to_cart(3))
        self.assertTrue(self.product.can_add_to_cart(5))
        
        # Test invalid quantity
        self.assertFalse(self.product.can_add_to_cart(6))
        self.assertFalse(self.product.can_add_to_cart(10))

    def test_cart_item_stock_validation(self):
        """Test that cart item creation respects stock limits"""
        # Test valid cart item creation
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        self.assertEqual(cart_item.quantity, 3)
        
        # Test invalid cart item creation (should raise exception)
        with self.assertRaises(ValueError):
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=10
            )

    def test_product_stock_status(self):
        """Test stock status messages"""
        # Test in stock
        self.assertEqual(self.product.get_stock_status(), "In Stock (5 available)")
        
        # Test low stock
        self.product.stock = 3
        self.product.save()
        self.assertEqual(self.product.get_stock_status(), "Only 3 left")
        
        # Test out of stock
        self.product.stock = 0
        self.product.save()
        self.assertEqual(self.product.get_stock_status(), "Out of Stock")

    def test_product_is_in_stock(self):
        """Test is_in_stock method"""
        # Test in stock
        self.assertTrue(self.product.is_in_stock())
        
        # Test out of stock
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock())
