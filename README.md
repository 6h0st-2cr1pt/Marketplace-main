# Local Marketplace

A dynamic e-commerce platform built with Django that connects local sellers with buyers. Features real-time analytics, order tracking, and a modern user interface.

## Features

### For Buyers
- 🛍️ Browse products by category and region
- 🔍 Advanced search functionality
- 🛒 Shopping cart management
- ❤️ Wishlist functionality
- 📦 Order tracking
- ⭐ Product reviews and ratings
- 💬 Contact sellers directly

### For Sellers
- 📝 Product management
- 📊 Sales tracking
- 📈 Performance analytics
- 📦 Order management
- 🏷️ Category management
- 📍 Regional targeting

### Admin Features
- 📊 Real-time analytics dashboard
  - Daily sales tracking
  - Product performance metrics
  - Category analytics
  - Customer insights
  - 30-day trends
- 👥 User management
- 🏪 Seller verification
- 📝 Content moderation

## Technology Stack

- **Backend**: Django 5.2
- **Database**: SQLite3
- **Frontend**: 
  - HTML5, CSS3, JavaScript
  - Bootstrap for responsive design
  - ECharts for data visualization
  - Flatpickr for date selection
- **Authentication**: Django Authentication System
- **File Storage**: Django File Storage
- **Email**: SMTP (Gmail)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Marketplace
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
Marketplace/
├── myproject/
│   ├── marketplace/
│   │   ├── management/
│   │   │   └── commands/
│   │   ├── migrations/
│   │   ├── static/
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── images/
│   │   ├── templates/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── myproject/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── manage.py
└── README.md
```

## Key Models

- **User**: Extended Django User model
- **Product**: Product information and inventory
- **Category**: Product categorization
- **Order/OrderItem**: Order management
- **Cart/CartItem**: Shopping cart functionality
- **Review**: Product reviews and ratings
- **Region/City**: Location management
- **SellerProfile**: Seller-specific information

## Analytics System

The platform includes a comprehensive analytics system that provides:

### Real-time Metrics
- Daily sales and revenue
- Order counts and trends
- Product performance
- Category insights
- Customer behavior

### Features
- Date-based filtering
- Seller-specific analytics
- Growth comparisons
- 30-day trend analysis
- Top performers tracking

### Data Visualization
- Interactive charts
- Tabular data
- Growth indicators
- Performance comparisons

## API Endpoints

### Product Management
- `GET /products/`: List all products
- `GET /products/<slug>/`: Product details
- `POST /products/`: Create product (sellers only)

### Order Management
- `GET /orders/`: List user orders
- `GET /orders/<id>/`: Order details
- `POST /orders/<id>/confirm-receipt/`: Confirm delivery

### Analytics
- `GET /admin/analytics-data/`: Get analytics data
  - Supports date and seller filtering
  - Returns comprehensive performance metrics

## Environment Variables

Create a `.env` file with:

```
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email [support@email.com](mailto:support@email.com) or create an issue in the repository.

## Acknowledgments

- Django Documentation
- Bootstrap Documentation
- ECharts Documentation
- Flatpickr
- Font Awesome
