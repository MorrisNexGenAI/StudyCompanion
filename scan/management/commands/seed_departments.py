from django.core.management.base import BaseCommand
from scan.models import Department

class Command(BaseCommand):
    help = 'Seed common departments'

    def handle(self, *args, **kwargs):
        departments = [
            'Health Science',
            'Criminal Justice',
            'Education',
            'Business',
            'Agriculture'
        ]
        
        for dept_name in departments:
            Department.objects.get_or_create(name=dept_name)
            self.stdout.write(f'✓ {dept_name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Seeded {len(departments)} departments!'))