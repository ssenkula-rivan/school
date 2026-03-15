"""
Create predefined education level templates
"""

from django.core.management.base import BaseCommand
from academics.models_levels import LevelPreset, LevelPresetItem


class Command(BaseCommand):
    help = 'Create predefined education level templates for different countries/systems'

    def handle(self, *args, **options):
        presets = [
            {
                'name': 'UK Education System',
                'country': 'United Kingdom',
                'levels': [
                    ('Nursery', 'early_years', 1, 'N', '3-4 years'),
                    ('Reception', 'early_years', 2, 'R', '4-5 years'),
                    ('Year 1', 'primary', 3, 'Y1', '5-6 years'),
                    ('Year 2', 'primary', 4, 'Y2', '6-7 years'),
                    ('Year 3', 'primary', 5, 'Y3', '7-8 years'),
                    ('Year 4', 'primary', 6, 'Y4', '8-9 years'),
                    ('Year 5', 'primary', 7, 'Y5', '9-10 years'),
                    ('Year 6', 'primary', 8, 'Y6', '10-11 years'),
                    ('Year 7', 'lower_secondary', 9, 'Y7', '11-12 years'),
                    ('Year 8', 'lower_secondary', 10, 'Y8', '12-13 years'),
                    ('Year 9', 'lower_secondary', 11, 'Y9', '13-14 years'),
                    ('Year 10 (GCSE)', 'upper_secondary', 12, 'Y10', '14-15 years'),
                    ('Year 11 (GCSE)', 'upper_secondary', 13, 'Y11', '15-16 years'),
                    ('Year 12 (A-Level)', 'upper_secondary', 14, 'Y12', '16-17 years'),
                    ('Year 13 (A-Level)', 'upper_secondary', 15, 'Y13', '17-18 years'),
                ]
            },
            {
                'name': 'US Education System',
                'country': 'United States',
                'levels': [
                    ('Preschool', 'early_years', 1, 'PS', '3-5 years'),
                    ('Kindergarten', 'early_years', 2, 'K', '5-6 years'),
                    ('Grade 1', 'primary', 3, 'G1', '6-7 years'),
                    ('Grade 2', 'primary', 4, 'G2', '7-8 years'),
                    ('Grade 3', 'primary', 5, 'G3', '8-9 years'),
                    ('Grade 4', 'primary', 6, 'G4', '9-10 years'),
                    ('Grade 5', 'primary', 7, 'G5', '10-11 years'),
                    ('Grade 6', 'lower_secondary', 8, 'G6', '11-12 years'),
                    ('Grade 7', 'lower_secondary', 9, 'G7', '12-13 years'),
                    ('Grade 8', 'lower_secondary', 10, 'G8', '13-14 years'),
                    ('Grade 9 (Freshman)', 'upper_secondary', 11, 'G9', '14-15 years'),
                    ('Grade 10 (Sophomore)', 'upper_secondary', 12, 'G10', '15-16 years'),
                    ('Grade 11 (Junior)', 'upper_secondary', 13, 'G11', '16-17 years'),
                    ('Grade 12 (Senior)', 'upper_secondary', 14, 'G12', '17-18 years'),
                ]
            },
            {
                'name': 'Uganda Education System',
                'country': 'Uganda',
                'levels': [
                    ('Baby Class', 'early_years', 1, 'BC', '3-4 years'),
                    ('Middle Class', 'early_years', 2, 'MC', '4-5 years'),
                    ('Top Class', 'early_years', 3, 'TC', '5-6 years'),
                    ('Primary 1', 'primary', 4, 'P1', '6-7 years'),
                    ('Primary 2', 'primary', 5, 'P2', '7-8 years'),
                    ('Primary 3', 'primary', 6, 'P3', '8-9 years'),
                    ('Primary 4', 'primary', 7, 'P4', '9-10 years'),
                    ('Primary 5', 'primary', 8, 'P5', '10-11 years'),
                    ('Primary 6', 'primary', 9, 'P6', '11-12 years'),
                    ('Primary 7', 'primary', 10, 'P7', '12-13 years'),
                    ('Senior 1 (O-Level)', 'lower_secondary', 11, 'S1', '13-14 years'),
                    ('Senior 2 (O-Level)', 'lower_secondary', 12, 'S2', '14-15 years'),
                    ('Senior 3 (O-Level)', 'lower_secondary', 13, 'S3', '15-16 years'),
                    ('Senior 4 (O-Level)', 'lower_secondary', 14, 'S4', '16-17 years'),
                    ('Senior 5 (A-Level)', 'upper_secondary', 15, 'S5', '17-18 years'),
                    ('Senior 6 (A-Level)', 'upper_secondary', 16, 'S6', '18-19 years'),
                ]
            },
            {
                'name': 'IB System',
                'country': 'International',
                'levels': [
                    ('PYP Year 1', 'primary', 1, 'PYP1', '5-6 years'),
                    ('PYP Year 2', 'primary', 2, 'PYP2', '6-7 years'),
                    ('PYP Year 3', 'primary', 3, 'PYP3', '7-8 years'),
                    ('PYP Year 4', 'primary', 4, 'PYP4', '8-9 years'),
                    ('PYP Year 5', 'primary', 5, 'PYP5', '9-10 years'),
                    ('PYP Year 6', 'primary', 6, 'PYP6', '10-11 years'),
                    ('MYP Year 1', 'lower_secondary', 7, 'MYP1', '11-12 years'),
                    ('MYP Year 2', 'lower_secondary', 8, 'MYP2', '12-13 years'),
                    ('MYP Year 3', 'lower_secondary', 9, 'MYP3', '13-14 years'),
                    ('MYP Year 4', 'lower_secondary', 10, 'MYP4', '14-15 years'),
                    ('MYP Year 5', 'lower_secondary', 11, 'MYP5', '15-16 years'),
                    ('DP Year 1', 'upper_secondary', 12, 'DP1', '16-17 years'),
                    ('DP Year 2', 'upper_secondary', 13, 'DP2', '17-18 years'),
                ]
            },
            {
                'name': 'University - 3 Year Degree',
                'country': 'International',
                'levels': [
                    ('Year 1', 'undergraduate', 1, 'Y1', '18+ years'),
                    ('Year 2', 'undergraduate', 2, 'Y2', '19+ years'),
                    ('Year 3', 'undergraduate', 3, 'Y3', '20+ years'),
                ]
            },
            {
                'name': 'University - 4 Year Degree',
                'country': 'International',
                'levels': [
                    ('Freshman Year', 'undergraduate', 1, 'Y1', '18+ years'),
                    ('Sophomore Year', 'undergraduate', 2, 'Y2', '19+ years'),
                    ('Junior Year', 'undergraduate', 3, 'Y3', '20+ years'),
                    ('Senior Year', 'undergraduate', 4, 'Y4', '21+ years'),
                ]
            },
        ]
        
        for preset_data in presets:
            preset, created = LevelPreset.objects.get_or_create(
                name=preset_data['name'],
                defaults={
                    'country': preset_data['country'],
                    'description': f"Standard {preset_data['name']} structure"
                }
            )
            
            if created:
                for name, level_type, order, code, age_range in preset_data['levels']:
                    LevelPresetItem.objects.create(
                        preset=preset,
                        name=name,
                        level_type=level_type,
                        order=order,
                        code=code,
                        age_range=age_range
                    )
                self.stdout.write(self.style.SUCCESS(f'Created preset: {preset.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Preset already exists: {preset.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal presets: {LevelPreset.objects.count()}'))
