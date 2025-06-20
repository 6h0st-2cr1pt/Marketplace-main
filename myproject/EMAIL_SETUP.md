# Email Setup for Local Marketplace

This document explains how to configure email functionality for the Local Marketplace application.

## Email Configuration

The application uses Django's built-in email functionality to send messages between buyers and sellers, with special handling for bulk and custom orders.

### 1. Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. **Update settings.py**:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   DEFAULT_FROM_EMAIL = 'Local Marketplace <your-email@gmail.com>'
   ADMIN_EMAIL = 'admin@yourdomain.com'  # Admin email for bulk orders
   ```

### 2. Development/Testing Setup

For development and testing, you can use the console backend which prints emails to the console:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Local Marketplace <noreply@localmarketplace.com>'
ADMIN_EMAIL = 'admin@localmarketplace.com'
```

### 3. Testing Email Functionality

Run the test commands to verify email setup:

```bash
python manage.py test_email
python manage.py test_bulk_order
```

## Features

### Contact Seller
- Buyers can send messages to product sellers
- Messages include product details and buyer information
- Both buyer and seller receive confirmation emails
- Form validation ensures proper message content

### Bulk/Custom Order Workflow
- **Bulk Orders**: For large quantities (10+ items)
- **Custom Orders**: For special requirements or modifications
- **Admin Processing**: All bulk/custom orders are sent to admin
- **Hardcopy Communication**: Admin contacts sellers via paper documents
- **Email Updates**: Buyers receive email confirmations and updates

### Message Types
1. **General Inquiry** - Sent directly to seller
2. **Bulk Order Request** - Sent to admin for processing
3. **Custom Order Request** - Sent to admin for processing
4. **Price Negotiation** - Sent directly to seller
5. **Shipping Information** - Sent directly to seller
6. **Other** - Sent directly to seller

### Email Templates
- Professional email formatting
- Product details included in messages
- Clear sender and recipient information
- Direct response capability
- Admin notification templates for bulk orders

## Workflow for Bulk/Custom Orders

1. **Buyer submits request** via contact form
2. **System identifies** bulk/custom order type
3. **Admin receives notification** with complete order details
4. **Admin processes request** and contacts seller via hardcopy
5. **Buyer receives confirmation** email with next steps
6. **Admin coordinates** between buyer and seller
7. **Updates sent** to buyer via email

## Security Considerations

1. **Never commit email credentials** to version control
2. **Use environment variables** for sensitive data in production
3. **Enable email validation** for user accounts
4. **Implement rate limiting** for message sending
5. **Add spam protection** for contact forms
6. **Secure admin email** for bulk order processing

## Production Deployment

For production, consider using:
- **SendGrid** for reliable email delivery
- **Amazon SES** for cost-effective email service
- **Mailgun** for developer-friendly email API

Update the email backend accordingly:

```python
# For SendGrid
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
ADMIN_EMAIL = 'admin@yourdomain.com'
```

## Admin Responsibilities

For bulk/custom orders, the admin should:

1. **Monitor admin email** for new requests
2. **Review order details** thoroughly
3. **Contact sellers** via hardcopy paper
4. **Coordinate communication** between parties
5. **Track order status** in the system
6. **Send updates** to buyers via email
7. **Ensure timely processing** of all requests

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check app password and 2FA settings
2. **Connection Timeout**: Verify firewall and network settings
3. **Email Not Received**: Check spam folder and email settings
4. **SMTP Error**: Verify port and TLS settings
5. **Admin Notifications**: Ensure ADMIN_EMAIL is configured correctly

### Debug Mode

Enable debug mode to see detailed error messages:

```python
DEBUG = True
```

## Support

For email-related issues, check:
- Django Email Documentation
- Gmail SMTP Settings
- Email Service Provider Documentation
- Bulk Order Workflow Documentation 