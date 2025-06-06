# Generated by Django 5.1.4 on 2025-03-01 13:24

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_purchasedproduct_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='treatmentdoctor',
            name='treatment',
        ),
        migrations.AlterField(
            model_name='treatmentdoctor',
            name='percent',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.CreateModel(
            name='TreatmentPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.TextField(blank=True, max_length=255, null=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_treatment_plan', to='core.patient')),
            ],
        ),
        migrations.CreateModel(
            name='TreatmentRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=100, null=True)),
                ('x_ray', models.BooleanField(default=False)),
                ('x_ray_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('lab', models.BooleanField(default=False)),
                ('lab_sent', models.CharField(blank=True, choices=[('Medi Dent Nepal', 'Medi Dent Nepal'), ('Proficient Dental Lab', 'Proficient Dental Lab'), ('Other', 'Other')], null=True)),
                ('lab_order_date', models.DateTimeField(blank=True, null=True)),
                ('lab_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('treatment_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('date_created', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_treatment_record', to='core.appointment')),
            ],
        ),
        migrations.AddField(
            model_name='treatmentdoctor',
            name='treatment_record',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='record_td', to='core.treatmentrecord'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Treatment',
        ),
    ]
