# Generated migration for curriculum and timezone fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_school_has_alevel_school_has_baby_care_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='curriculum',
            field=models.CharField(
                choices=[
                    ('uganda_primary', 'Uganda Primary Curriculum (P1-P7)'),
                    ('uganda_olevel', 'Uganda O-Level Curriculum (S1-S4)'),
                    ('uganda_alevel', 'Uganda A-Level Curriculum (S5-S6)'),
                    ('uganda_thematic', 'Uganda Thematic Curriculum (Lower Primary)'),
                    ('uganda_btvet', 'Uganda BTVET Curriculum'),
                    ('cambridge_primary', 'Cambridge Primary Programme'),
                    ('cambridge_lower_secondary', 'Cambridge Lower Secondary'),
                    ('cambridge_igcse', 'Cambridge IGCSE (O-Level)'),
                    ('cambridge_as_a_level', 'Cambridge AS & A Level'),
                    ('ib_pyp', 'IB Primary Years Programme (PYP)'),
                    ('ib_myp', 'IB Middle Years Programme (MYP)'),
                    ('ib_dp', 'IB Diploma Programme (DP)'),
                    ('british_national', 'British National Curriculum'),
                    ('american_curriculum', 'American Curriculum'),
                    ('montessori', 'Montessori Method'),
                    ('eac_curriculum', 'East African Community Curriculum'),
                    ('kenyan_curriculum', 'Kenyan Curriculum (CBC)'),
                    ('tanzanian_curriculum', 'Tanzanian Curriculum'),
                    ('rwandan_curriculum', 'Rwandan Curriculum'),
                    ('custom', 'Custom/Mixed Curriculum'),
                ],
                default='uganda_primary',
                help_text='Primary curriculum system used by the school',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='school',
            name='secondary_curriculum',
            field=models.CharField(
                blank=True,
                choices=[
                    ('uganda_primary', 'Uganda Primary Curriculum (P1-P7)'),
                    ('uganda_olevel', 'Uganda O-Level Curriculum (S1-S4)'),
                    ('uganda_alevel', 'Uganda A-Level Curriculum (S5-S6)'),
                    ('uganda_thematic', 'Uganda Thematic Curriculum (Lower Primary)'),
                    ('uganda_btvet', 'Uganda BTVET Curriculum'),
                    ('cambridge_primary', 'Cambridge Primary Programme'),
                    ('cambridge_lower_secondary', 'Cambridge Lower Secondary'),
                    ('cambridge_igcse', 'Cambridge IGCSE (O-Level)'),
                    ('cambridge_as_a_level', 'Cambridge AS & A Level'),
                    ('ib_pyp', 'IB Primary Years Programme (PYP)'),
                    ('ib_myp', 'IB Middle Years Programme (MYP)'),
                    ('ib_dp', 'IB Diploma Programme (DP)'),
                    ('british_national', 'British National Curriculum'),
                    ('american_curriculum', 'American Curriculum'),
                    ('montessori', 'Montessori Method'),
                    ('eac_curriculum', 'East African Community Curriculum'),
                    ('kenyan_curriculum', 'Kenyan Curriculum (CBC)'),
                    ('tanzanian_curriculum', 'Tanzanian Curriculum'),
                    ('rwandan_curriculum', 'Rwandan Curriculum'),
                    ('custom', 'Custom/Mixed Curriculum'),
                ],
                help_text='Secondary curriculum (for schools with multiple levels)',
                max_length=50
            ),
        ),
        migrations.AlterField(
            model_name='school',
            name='timezone',
            field=models.CharField(
                choices=[
                    ('Africa/Kampala', 'East Africa Time (EAT) - Uganda, Kenya, Tanzania'),
                    ('Africa/Nairobi', 'East Africa Time (EAT) - Kenya'),
                    ('Africa/Dar_es_Salaam', 'East Africa Time (EAT) - Tanzania'),
                    ('Africa/Kigali', 'Central Africa Time (CAT) - Rwanda'),
                    ('Africa/Lagos', 'West Africa Time (WAT) - Nigeria'),
                    ('Africa/Johannesburg', 'South Africa Standard Time (SAST)'),
                    ('Europe/London', 'Greenwich Mean Time (GMT) - UK'),
                    ('America/New_York', 'Eastern Time (ET) - USA'),
                    ('Asia/Dubai', 'Gulf Standard Time (GST) - UAE'),
                    ('UTC', 'Coordinated Universal Time (UTC)'),
                ],
                default='Africa/Kampala',
                help_text='School timezone for scheduling and reports',
                max_length=50
            ),
        ),
    ]
