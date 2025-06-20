from .models import Category

def footer_categories(request):
    return {'footer_categories': Category.objects.all()} 