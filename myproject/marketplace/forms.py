from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Review, ProductImage
import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import os
import base64
import re

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
        })
    )
    
    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if product:
            self.fields['quantity'].widget.attrs['max'] = product.stock
            self.fields['quantity'].help_text = f'Maximum {product.stock} items available'
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if hasattr(self, 'product') and self.product:
            if quantity > self.product.stock:
                raise forms.ValidationError(f'Only {self.product.stock} items available in stock.')
        return quantity

class ContactSellerForm(forms.Form):
    MESSAGE_TYPE_CHOICES = [
        ('general', 'General Inquiry'),
        ('bulk_order', 'Bulk Order Request'),
        ('custom_order', 'Custom Order Request'),
        ('price_negotiation', 'Price Negotiation'),
        ('shipping_info', 'Shipping Information'),
        ('other', 'Other'),
    ]
    
    message_type = forms.ChoiceField(
        choices=MESSAGE_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        initial='general'
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject of your message'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Write your message here...'
        })
    )
    
    buyer_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )
    
    buyer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        })
    )
    
    # Additional fields for bulk/custom orders
    quantity = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quantity needed (for bulk orders)',
            'min': '1'
        })
    )
    
    delivery_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Preferred delivery date'
        })
    )
    
    special_requirements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requirements or customizations...'
        })
    )
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject.strip()) < 3:
            raise forms.ValidationError('Subject must be at least 3 characters long.')
        return subject
    
    def clean(self):
        cleaned_data = super().clean()
        message_type = cleaned_data.get('message_type')
        quantity = cleaned_data.get('quantity')
        delivery_date = cleaned_data.get('delivery_date')
        
        # Validate bulk order requirements
        if message_type in ['bulk_order', 'custom_order']:
            if not quantity:
                self.add_error('quantity', 'Quantity is required for bulk/custom orders.')
            if not delivery_date:
                self.add_error('delivery_date', 'Delivery date is required for bulk/custom orders.')
        
        return cleaned_data 

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES, attrs={'class': 'form-check-inline'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your thoughts about this product...'})
        }
        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Review (optional)'
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            raise forms.ValidationError('Please select a rating.')
        return rating 

class ProductImageAdminForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False  # Make image field optional

    def clean(self):
        cleaned_data = super().clean()
        image_url = cleaned_data.get('image_url')
        image = cleaned_data.get('image')
        if not image and not image_url:
            raise forms.ValidationError('You must provide either an image file or an image URL.')
        if image_url:
            # Check for data URL (base64)
            data_url_pattern = re.compile(r'^data:image/(?P<ext>\w+);base64,(?P<data>.+)$')
            match = data_url_pattern.match(image_url)
            if match:
                ext = match.group('ext')
                data = match.group('data')
                try:
                    file_data = base64.b64decode(data)
                    file_name = f"uploaded_image.{ext}"
                    cleaned_data['image'] = ContentFile(file_data, name=file_name)
                except Exception as e:
                    raise forms.ValidationError(f'Failed to decode base64 image: {e}')
            else:
                # Standard URL
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()
                    file_name = os.path.basename(urlparse(image_url).path)
                    if not file_name:
                        file_name = 'downloaded_image.jpg'
                    cleaned_data['image'] = ContentFile(response.content, name=file_name)
                except Exception as e:
                    raise forms.ValidationError(f'Failed to download image from URL: {e}')
        return cleaned_data 