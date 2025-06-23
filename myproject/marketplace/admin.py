from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, Wishlist, Region, City, Review, SellerProfile
from .forms import ProductImageAdminForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import openpyxl
from django.http import HttpResponse
from django.db.models import Count, Sum

User = get_user_model()

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('product', 'user', 'created_at') # Prevent changing review details after submission
    list_editable = ('rating',)
    actions = ['delete_selected']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'created_at')
    list_filter = ('region', 'created_at')
    search_fields = ('name', 'region__name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image', 'image_url', 'unit', 'created_at', 'is_primary', 'preview_image')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    fields = ('name', 'slug', 'description', 'image', 'image_url', 'unit', 'is_primary', 'preview_image')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="60" height="60" style="object-fit:cover;" />'
        elif obj.image_url:
            return f'<img src="{obj.image_url}" width="60" height="60" style="object-fit:cover;" />'
        return "No Image"
    preview_image.short_description = 'Preview'
    preview_image.allow_tags = True

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'image_url', 'is_primary', 'preview_image')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" style="object-fit: cover;" />'
        return "No Image"
    preview_image.short_description = 'Preview'
    preview_image.allow_tags = True

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'stock', 'region', 'city', 'is_active', 'display_average_rating', 'display_review_count', 'created_at', 'preview_image')
    list_filter = ('category', 'region', 'city', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'seller__username', 'location')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'price')
        }),
        ('Location Information', {
            'fields': ('region', 'city', 'location'),
            'description': 'Product location details'
        }),
        ('Stock Level', {
            'fields': ('stock', 'is_active'),
            'description': 'Manage product stock and availability'
        }),
        ('Seller Information', {
            'fields': ('seller',),
            'classes': ('collapse',)
        }),
    )

    def preview_image(self, obj):
        primary_image = obj.get_primary_image()
        if primary_image:
            return f'<img src="{primary_image.url}" width="50" height="50" style="object-fit: cover;" />'
        return "No Image"
    preview_image.short_description = 'Image'
    preview_image.allow_tags = True

    def display_average_rating(self, obj):
        average_rating = obj.get_average_rating()
        if average_rating > 0:
            # Render stars for average rating
            stars = ''.join(['<i class="fas fa-star text-warning small"></i>' for _ in range(int(average_rating))])
            if average_rating - int(average_rating) >= 0.5:
                stars += '<i class="fas fa-star-half-alt text-warning small"></i>'
            remaining_stars = 5 - len(stars.split('star')) + 1 # Calculate remaining empty stars
            stars += ''.join(['<i class="far fa-star text-warning small"></i>' for _ in range(remaining_stars)])
            return f"{stars} ({average_rating:.1f})"
        return "N/A"
    display_average_rating.short_description = 'Avg. Rating'
    display_average_rating.admin_order_field = 'rating__avg' # Allows sorting by average rating
    display_average_rating.allow_tags = True

    def display_review_count(self, obj):
        return obj.get_review_count()
    display_review_count.short_description = 'Reviews'
    display_review_count.admin_order_field = 'review_count' # Allows sorting by review count

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    form = ProductImageAdminForm
    list_display = ('product', 'display_image', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name',)
    
    def display_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />'
        return "No Image"
    display_image.short_description = 'Image'
    display_image.allow_tags = True

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__username', 'product__name')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'shipping_address')
    actions = ['export_selected_orders_to_excel']

    def export_selected_orders_to_excel(self, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Orders"

        # Header row
        ws.append([
            "Order ID", "Buyer", "First Name", "Last Name", "Email", "Address", "Phone",
            "Status", "Payment Method", "Total Price", "Created At", "Product", "Seller Name", "Seller Address", "Seller Region"
        ])

        for order in queryset:
            for item in order.items.all():
                seller_profile = getattr(item.product.seller, 'seller_profile', None)
                seller_name = seller_profile.name if seller_profile else item.product.seller.get_full_name() or item.product.seller.username
                seller_address = seller_profile.address if seller_profile else ''
                seller_region = item.product.region.get_name_display() if hasattr(item.product, 'region') and item.product.region else ''
                ws.append([
                    order.id,
                    order.user.username,
                    order.first_name,
                    order.last_name,
                    order.email,
                    order.address,
                    order.phone,
                    order.get_status_display(),
                    order.get_payment_method_display(),
                    float(order.total_price),
                    order.created_at.strftime("%Y-%m-%d %H:%M"),
                    item.product.name,
                    seller_name,
                    seller_address,
                    seller_region,
                ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
        wb.save(response)
        return response

    export_selected_orders_to_excel.short_description = "Export selected orders to Excel"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__user__username', 'product__name')

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'address', 'profile_pic_preview')
    search_fields = ('user__username', 'name', 'address')
    readonly_fields = ('profile_pic_preview',)
    list_filter = ('user',)
    
    def profile_pic_preview(self, obj):
        if obj.profile_pic:
            return f'<img src="{obj.profile_pic.url}" width="50" height="50" style="object-fit: cover;" />'
        return "No Image"
    profile_pic_preview.short_description = 'Profile Pic'
    profile_pic_preview.allow_tags = True

class SellerProfileFilter(admin.SimpleListFilter):
    title = _('Seller/Buyer')
    parameter_name = 'is_seller'

    def lookups(self, request, model_admin):
        return (
            ('seller', _('Seller')),
            ('buyer', _('Buyer')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'seller':
            return queryset.filter(seller_profile__isnull=False)
        if self.value() == 'buyer':
            return queryset.filter(seller_profile__isnull=True)
        return queryset

# Unregister the default User admin and register with the new filter
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_filter = UserAdmin.list_filter + (SellerProfileFilter,)

# Add the analytics endpoint to admin URLs
admin_urls = [
]
try:
    admin.site.get_urls = (lambda get_urls: lambda: admin_urls + get_urls())(admin.site.get_urls)
except Exception:
    pass
