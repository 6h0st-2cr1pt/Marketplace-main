from django.core.management.base import BaseCommand
from marketplace.models import Region, City
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate the database with sample regions and cities'

    def handle(self, *args, **options):
        self.stdout.write('Creating regions and cities...')
        
        # Create regions
        regions_data = [
            {
                'name': 'luzon',
                'description': 'The largest and most populous island in the Philippines, home to the capital Manila and many major cities.',
                'cities': [
                    'Manila', 'Quezon City', 'Caloocan', 'Las Piñas', 'Makati', 'Malabon', 'Mandaluyong', 'Marikina',
                    'Muntinlupa', 'Navotas', 'Parañaque', 'Pasay', 'Pasig', 'San Juan', 'Taguig', 'Valenzuela',
                    'Antipolo', 'Bacoor', 'Cabuyao', 'Calamba', 'Cavite City', 'Dasmariñas', 'Imus', 'San Pedro',
                    'Santa Rosa', 'Tagaytay', 'Trece Martires', 'Baguio', 'Dagupan', 'San Fernando', 'Tarlac City',
                    'Angeles', 'Olongapo', 'Batangas City', 'Lipa', 'San Pablo', 'Lucena', 'Naga', 'Legazpi',
                    'Iriga', 'Tabaco', 'Ligao', 'Sorsogon City', 'Masbate City', 'Puerto Princesa', 'Calapan',
                    'San Jose', 'Boac', 'Romblon', 'Virac', 'Catanduanes'
                ]
            },
            {
                'name': 'visayas',
                'description': 'The central island group of the Philippines, known for its beautiful beaches and rich cultural heritage.',
                'cities': [
                    'Cebu City', 'Mandaue', 'Lapu-Lapu', 'Talisay', 'Toledo', 'Carcar', 'Naga', 'Danao',
                    'Bacolod', 'Silay', 'Victorias', 'Cadiz', 'Sagay', 'Escalante', 'San Carlos',
                    'Iloilo City', 'Passi', 'Roxas', 'Kalibo', 'Boracay', 'Tagbilaran',
                    'Tacloban', 'Ormoc', 'Baybay', 'Maasin', 'Catbalogan', 'Calbayog', 'Catarman',
                    'Dumaguete', 'Bais', 'Tanjay', 'Bayawan', 'Canlaon', 'Guihulngan',
                    'Tubigon', 'Jagna', 'Ubay', 'Talibon', 'Candijay', 'Alicia'
                ]
            },
            {
                'name': 'mindanao',
                'description': 'The southernmost major island group, known for its diverse culture and natural resources.',
                'cities': [
                    'Davao City', 'Digos', 'Mati', 'Tagum', 'Panabo', 'Island Garden City of Samal',
                    'Cagayan de Oro', 'Iligan', 'Oroquieta', 'Ozamiz', 'Tangub', 'Gingoog', 'Camiguin',
                    'Zamboanga City', 'Dipolog', 'Pagadian', 'Ipil', 'Isabela', 'Lamitan', 'Cotabato City',
                    'Kidapawan', 'Koronadal', 'Tacurong', 'General Santos', 'Butuan', 'Surigao City',
                    'Tandag', 'Bislig', 'Bayugan', 'Cabadbaran', 'Marawi', 'Jolo', 'Bongao'
                ]
            }
        ]
        
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                name=region_data['name'],
                defaults={'description': region_data['description']}
            )
            
            if created:
                self.stdout.write(f'Created region: {region.get_name_display()}')
            else:
                self.stdout.write(f'Region already exists: {region.get_name_display()}')
            
            # Create cities for this region
            for city_name in region_data['cities']:
                # Create a unique slug by combining city name and region
                base_slug = slugify(city_name)
                slug = f"{base_slug}-{region.name}"
                
                city, created = City.objects.get_or_create(
                    name=city_name,
                    region=region,
                    defaults={'slug': slug}
                )
                
                if created:
                    self.stdout.write(f'  Created city: {city_name}')
                else:
                    self.stdout.write(f'  City already exists: {city_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated regions and cities!')
        ) 