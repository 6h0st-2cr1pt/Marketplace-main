from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import Product, Category, Cart, CartItem, Wishlist, Order, OrderItem, Region, City, Review, User
from .forms import UserRegistrationForm, AddToCartForm, ContactSellerForm, ReviewForm
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from datetime import timedelta
import json
import calendar
import logging

def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    categories = Category.objects.all()[:6]  # Limit to 6 categories
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category', 'region', 'city')
    # Debug print to check stock values
    print("\nProduct Stock Levels:")
    for product in products:
        print(f"Product: {product.name}, Stock: {product.stock}")
    print("\n")
    
    categories = Category.objects.all()
    regions = Region.objects.all()
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Filter by region
    region_slug = request.GET.get('region')
    if region_slug:
        products = products.filter(region__slug=region_slug)
    
    # Filter by city
    city_slug = request.GET.get('city')
    if city_slug:
        products = products.filter(city__slug=city_slug)
    
    # Sort products
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'regions': regions,
    }
    return render(request, 'products.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Debugging the user and seller IDs
    print(f"DEBUG in product_detail: User Authenticated: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        print(f"DEBUG in product_detail: Logged in User ID: {request.user.id}")
    print(f"DEBUG in product_detail: Product Seller ID: {product.seller.id}")

    # Handle review submission
    review_form = None
    user_has_reviewed = False
    user_has_in_wishlist = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
        user_has_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
        if not user_has_reviewed:
            if request.method == 'POST' and 'review_submit' in request.POST: # Check for review form submission
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.product = product
                    review.user = request.user
                    review.save()
                    messages.success(request, 'Your review has been submitted successfully!')
                    return redirect('marketplace:product_detail', slug=product.slug)
            else:
                review_form = ReviewForm()

    # Get existing reviews for the product
    reviews = product.reviews.all()

    # Create form for quantity validation
    add_to_cart_form = AddToCartForm(product=product)
    
    context = {
        'product': product,
        'related_products': related_products,
        'add_to_cart_form': add_to_cart_form,
        'user': request.user,  # Ensure user is available in template
        'review_form': review_form,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed,
        'user_has_in_wishlist': user_has_in_wishlist,
    }
    return render(request, 'product_detail.html', context)

def category_list(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'marketplace/category_list.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Sort products
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Filter by condition
    condition = request.GET.get('condition')
    if condition:
        products = products.filter(condition=condition)
    
    context = {
        'category': category,
        'products': products,
        'condition_choices': Product.CONDITION_CHOICES,
    }
    return render(request, 'category_detail.html', context)

def region_list(request):
    """Display all regions with product counts"""
    regions = Region.objects.all()
    for region in regions:
        region.product_count = region.products.filter(is_active=True).count()
    
    context = {
        'regions': regions,
    }
    return render(request, 'marketplace/region_list.html', context)

def region_detail(request, slug):
    """Display products filtered by region"""
    region = get_object_or_404(Region, slug=slug)
    products = Product.objects.filter(region=region, is_active=True).select_related('category', 'city')
    
    # Search within region
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Filter by city within region
    city_slug = request.GET.get('city')
    if city_slug:
        products = products.filter(city__slug=city_slug)
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Sort products
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    # Get cities in this region for filtering
    cities = region.cities.all()
    categories = Category.objects.all()
    
    context = {
        'region': region,
        'products': products,
        'cities': cities,
        'categories': categories,
    }
    return render(request, 'marketplace/region_detail.html', context)

def city_detail(request, slug):
    """Display products filtered by city"""
    city = get_object_or_404(City, slug=slug)
    products = Product.objects.filter(city=city, is_active=True).select_related('category', 'region')
    
    # Search within city
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Sort products
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    categories = Category.objects.all()
    
    context = {
        'city': city,
        'products': products,
        'categories': categories,
    }
    return render(request, 'marketplace/city_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    else:
        products = Product.objects.none()
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'search_results.html', context)

@login_required
def cart(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    cart_items = cart.items.all()
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Use form validation
    form = AddToCartForm(product=product, data=request.POST)
    if not form.is_valid():
        for error in form.errors.values():
            messages.error(request, error[0])
        return redirect('marketplace:product_detail', slug=product.slug)
    
    quantity = form.cleaned_data['quantity']
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f'Cannot add more items. Only {product.stock} items available in stock.')
            return redirect('marketplace:product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
    else:
        cart_item.quantity = quantity
    
    cart_item.save()
    messages.success(request, f'{product.name} added to cart.')
    return redirect('marketplace:cart')

@login_required
@require_POST
def update_cart_item(request, item_id):
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        
        if action == 'increase':
            # Check if increasing quantity would exceed stock
            if cart_item.quantity >= cart_item.product.stock:
                return JsonResponse({
                    'success': False, 
                    'message': f'Cannot add more items. Only {cart_item.product.stock} items available in stock.'
                })
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                return JsonResponse({'success': True})
        
        cart_item.save()
        return JsonResponse({'success': True})
    except (CartItem.DoesNotExist, json.JSONDecodeError):
        return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False}, status=400)

@login_required
def checkout(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('marketplace:cart')
    
    # Validate stock levels before checkout
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f'Not enough stock for {item.product.name}. Only {item.product.stock} items available.')
            return redirect('marketplace:cart')
    
    if request.method == 'POST':
        # Process the order
        full_name = request.POST.get('full_name', '').split(' ', 1)
        first_name = full_name[0] if full_name else ''
        last_name = full_name[1] if len(full_name) > 1 else ''

        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            phone=request.POST.get('phone'),
            payment_method=request.POST.get('payment_method'),
            total_price=cart.get_total_price()
        )
        
        # Create order items and update product stock
        for item in cart.items.all():
            order.items.create(
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
            # Update product stock
            item.product.stock -= item.quantity
            item.product.save()
        
        # Clear the cart
        cart.items.all().delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('marketplace:order_detail', order_id=order.id)
    
    return render(request, 'marketplace/checkout.html', {'cart': cart})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'marketplace/order_detail.html', {
        'order': order
    })

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/orders.html', {
        'orders': orders
    })

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'marketplace/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to wishlist!'
        })
    
    # Regular request - redirect with message
    messages.success(request, f'{product.name} added to wishlist!')
    return redirect('marketplace:wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Item removed from wishlist!'
        })
    
    # Regular request - redirect with message
    messages.success(request, 'Item removed from wishlist!')
    return redirect('marketplace:wishlist')

@login_required
def profile(request):
    return render(request, 'marketplace/profile.html')

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'orders.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Local Marketplace.')
            return redirect('marketplace:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# API Views
@login_required
def api_add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'cart_count': cart.get_total_items(),
                'message': 'Product added to cart successfully!'
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def api_toggle_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            wishlist_item.delete()
            return JsonResponse({'status': 'removed'})
        
        return JsonResponse({'status': 'added'})
    
    return JsonResponse({'status': 'error'}, status=400)

def api_search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )[:5]
        
        results = [{
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image': product.image.url,
            'slug': product.slug
        } for product in products]
        
        return JsonResponse({
            'success': True,
            'results': results
        })
    
    return JsonResponse({
        'success': False,
        'message': 'No query provided'
    })

def api_cities(request):
    """API endpoint to get cities by region"""
    region_slug = request.GET.get('region')
    if region_slug:
        try:
            region = Region.objects.get(slug=region_slug)
            cities = region.cities.all()
            cities_data = [{
                'id': city.id,
                'name': city.name,
                'slug': city.slug
            } for city in cities]
            
            return JsonResponse({
                'success': True,
                'cities': cities_data
            })
        except Region.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Region not found'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Region parameter required'
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is not an admin
            if not user.is_staff and not user.is_superuser:
                login(request, user)
                messages.success(request, 'Successfully logged in!')
                return redirect('marketplace:home')
            else:
                messages.error(request, 'Admin users cannot login to the marketplace.')
                return redirect('marketplace:login')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('marketplace:login')
            
    return render(request, 'marketplace/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('marketplace:home')

def contact_seller(request, product_id):
    """Contact seller about a specific product"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.method == 'POST':
        form = ContactSellerForm(request.POST)
        if form.is_valid():
            # Get form data
            buyer_name = form.cleaned_data['buyer_name']
            buyer_email = form.cleaned_data['buyer_email']
            message_type = form.cleaned_data['message_type']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            quantity = form.cleaned_data.get('quantity')
            delivery_date = form.cleaned_data.get('delivery_date')
            special_requirements = form.cleaned_data.get('special_requirements')
            
            # Determine if this is a bulk/custom order that should go to admin
            is_admin_request = message_type in ['bulk_order', 'custom_order']

            print(f"DEBUG: Message Type: {message_type}, Is Admin Request: {is_admin_request}") # DEBUG

            if is_admin_request:
                # Send to admin for processing
                admin_subject = f"BULK/CUSTOM ORDER REQUEST - {product.name}"
                
                admin_body = f"""
ADMIN NOTIFICATION - BULK/CUSTOM ORDER REQUEST

A buyer has submitted a {message_type.replace('_', ' ').title()} request that requires your attention.

BUYER DETAILS:
- Name: {buyer_name}
- Email: {buyer_email}
- Message Type: {message_type.replace('_', ' ').title()}

PRODUCT DETAILS:
- Product: {product.name}
- Seller: {product.seller.first_name or product.seller.username} ({product.seller.email})
- Current Price: ₱{product.price}
- Product URL: {request.build_absolute_uri(product.get_absolute_url())}

ORDER DETAILS:
- Quantity Requested: {quantity or 'Not specified'}
- Preferred Delivery Date: {delivery_date or 'Not specified'}
- Special Requirements: {special_requirements or 'None'}

BUYER MESSAGE:
Subject: {subject}
Message: {message}

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
                
                # Send email to admin (you can configure admin email in settings)
                admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@localmarketplace.com')
                print(f"DEBUG: Admin Email Recipient: {admin_email}") # DEBUG
                
                try:
                    send_mail(
                        subject=admin_subject,
                        message=admin_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[admin_email],
                        fail_silently=False,
                    )
                    
                    # Send confirmation to buyer
                    buyer_subject = f"Bulk/Custom Order Request Received - {product.name}"
                    buyer_body = f"""
Hello {buyer_name},

Thank you for your {message_type.replace('_', ' ').title()} request for "{product.name}".

Your request has been received and is being processed by our admin team.

REQUEST SUMMARY:
- Product: {product.name}
- Quantity: {quantity or 'Not specified'}
- Delivery Date: {delivery_date or 'Not specified'}
- Special Requirements: {special_requirements or 'None'}

Your message: {message}

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
                        recipient_list=[buyer_email],
                        fail_silently=False,
                    )
                    
                    messages.success(request, f'Your {message_type.replace("_", " ").title()} request has been sent to our admin team. They will process your request and contact you soon.')
                    
                except Exception as e:
                    messages.error(request, f'Failed to send request. Please try again later. Error: {str(e)}')
                
            else:
                # Regular inquiry - send directly to seller
                email_subject = f"Message about {product.name} - {subject}"
                
                email_body = f"""
Hello {product.seller.first_name or product.seller.username},

You have received a message from a potential buyer about your product "{product.name}".

Buyer Details:
- Name: {buyer_name}
- Email: {buyer_email}
- Message Type: {message_type.replace('_', ' ').title()}

Message:
{message}

Product Details:
- Product: {product.name}
- Price: ₱{product.price}
- URL: {request.build_absolute_uri(product.get_absolute_url())}

Please respond directly to the buyer at: {buyer_email}

Best regards,
Local Marketplace Team
                """
                
                try:
                    send_mail(
                        subject=email_subject,
                        message=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[product.seller.email],
                        fail_silently=False,
                    )
                    
                    # Send confirmation email to buyer
                    buyer_subject = f"Message sent about {product.name}"
                    buyer_body = f"""
Hello {buyer_name},

Thank you for contacting the seller about "{product.name}".

Your message has been sent successfully to {product.seller.first_name or product.seller.username}.

Your message:
{message}

The seller will respond to you directly at: {buyer_email}

Best regards,
Local Marketplace Team
                    """
                    
                    send_mail(
                        subject=buyer_subject,
                        message=buyer_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[buyer_email],
                        fail_silently=False,
                    )
                    
                    messages.success(request, 'Your message has been sent successfully! The seller will respond to you directly.')
                    
                except Exception as e:
                    messages.error(request, f'Failed to send message. Please try again later. Error: {str(e)}')
            
            return redirect('marketplace:product_detail', slug=product.slug)
        else:
            print(f"DEBUG: Form errors: {form.errors}") # DEBUG
            # Form is invalid, it will fall through to render the form again with errors
    else: # GET request
        # Pre-fill form with user data if logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'buyer_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'buyer_email': request.user.email,
            }
        form = ContactSellerForm(initial=initial_data)

    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'marketplace/contact_seller.html', context)

@login_required
def confirm_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'shipped':
        order.status = 'delivered'
        order.save()
        messages.success(request, 'Thank you for confirming receipt! You can now rate your product(s).')
    return redirect('marketplace:order_detail', order_id=order.id)

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_home(request):
    """Admin dashboard home view"""
    return render(request, 'admin/home.html')

@user_passes_test(is_admin)
def admin_analytics_data(request):
    """Real-time analytics data for admin dashboard"""
    try:
        from django.http import JsonResponse
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        # Get date filter from request
        date_str = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
        seller_filter = request.GET.get('seller', '')
        
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
        
        # Calculate date ranges
        yesterday = selected_date - timedelta(days=1)
        
        # Base querysets - include all orders, not just delivered
        orders_today = Order.objects.filter(created_at__date=selected_date)
        orders_yesterday = Order.objects.filter(created_at__date=yesterday)
        
        # Apply seller filter if specified
        if seller_filter:
            orders_today = orders_today.filter(items__product__seller__username=seller_filter).distinct()
            orders_yesterday = orders_yesterday.filter(items__product__seller__username=seller_filter).distinct()
        
        # Summary metrics for selected date
        today_sales = orders_today.aggregate(total=Sum('total_price'))['total'] or 0
        today_orders = orders_today.count()
        today_items = OrderItem.objects.filter(order__in=orders_today).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Yesterday metrics for comparison
        yesterday_sales = orders_yesterday.aggregate(total=Sum('total_price'))['total'] or 0
        yesterday_orders = orders_yesterday.count()
        
        # Calculate growth percentages
        sales_growth = ((today_sales - yesterday_sales) / yesterday_sales * 100) if yesterday_sales > 0 else 0
        orders_growth = ((today_orders - yesterday_orders) / yesterday_orders * 100) if yesterday_orders > 0 else 0
        
        # Other metrics
        active_products = Product.objects.filter(is_active=True).count()
        total_users = User.objects.count()
        avg_order_value = today_sales / today_orders if today_orders > 0 else 0
        
        # 30-day trend data
        trend_data = []
        for i in range(30):
            date = selected_date - timedelta(days=i)
            day_orders = Order.objects.filter(created_at__date=date)
            if seller_filter:
                day_orders = day_orders.filter(items__product__seller__username=seller_filter).distinct()
            
            day_sales = day_orders.aggregate(total=Sum('total_price'))['total'] or 0
            day_order_count = day_orders.count()
            day_avg_order = day_sales / day_order_count if day_order_count > 0 else 0
            
            trend_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(day_sales),
                'orders': day_order_count,
                'avg_order_value': float(day_avg_order)
            })
        
        # Reverse to show oldest to newest
        trend_data.reverse()
        
        # Top products for selected date
        top_products = (
            OrderItem.objects
            .filter(order__created_at__date=selected_date)
            .values('product__name', 'product__category__name')
            .annotate(
                total_sales=Sum('price'),
                units_sold=Sum('quantity')
            )
            .order_by('-total_sales')[:10]
        )
        
        # Category performance
        category_data = (
            OrderItem.objects
            .filter(order__created_at__date=selected_date)
            .values('product__category__name')
            .annotate(
                sales=Sum('price'),
                units=Sum('quantity')
            )
            .order_by('-sales')
        )
        
        # Top sellers
        top_sellers = (
            OrderItem.objects
            .filter(order__created_at__date=selected_date)
            .values('product__seller__username')
            .annotate(
                total_sales=Sum('price'),
                order_count=Count('order', distinct=True)
            )
            .annotate(avg_order_value=Sum('price') / Count('order', distinct=True))
            .order_by('-total_sales')[:10]
        )
        
        # Top customers
        top_customers = (
            Order.objects
            .filter(created_at__date=selected_date)
            .values('user__username')
            .annotate(
                total_spent=Sum('total_price'),
                order_count=Count('id')
            )
            .annotate(avg_order_value=Sum('total_price') / Count('id'))
            .order_by('-total_spent')[:10]
        )
        
        response_data = {
            'summary': {
                'total_sales': float(today_sales),
                'total_orders': today_orders,
                'items_sold': today_items,
                'active_products': active_products,
                'total_users': total_users,
                'avg_order_value': float(avg_order_value),
                'yesterday_sales': float(yesterday_sales),
                'yesterday_orders': yesterday_orders,
                'sales_growth': float(sales_growth),
                'orders_growth': float(orders_growth)
            },
            'dates': [item['date'] for item in trend_data],
            'revenue': [item['revenue'] for item in trend_data],
            'orders': [item['orders'] for item in trend_data],
            'avg_order_values': [item['avg_order_value'] for item in trend_data],
            'product_data': list(top_products),
            'category_data': {
                'categories': [item['product__category__name'] for item in category_data],
                'sales': [float(item['sales']) for item in category_data],
                'units': [item['units'] for item in category_data],
                'growth': [0.0] * len(category_data)  # Simplified growth calculation
            },
            'seller_data': list(top_sellers),
            'customer_data': list(top_customers)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        print(f"Error in admin_analytics_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'error': str(e),
            'summary': {
                'total_sales': 0.0,
                'total_orders': 0,
                'items_sold': 0,
                'active_products': 0,
                'total_users': 0,
                'avg_order_value': 0.0,
                'yesterday_sales': 0.0,
                'yesterday_orders': 0,
                'sales_growth': 0.0,
                'orders_growth': 0.0
            },
            'dates': [],
            'revenue': [],
            'orders': [],
            'avg_order_values': [],
            'product_data': [],
            'category_data': {
                'categories': [],
                'sales': [],
                'units': [],
                'growth': []
            },
            'seller_data': [],
            'customer_data': []
        })
