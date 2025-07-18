# Generated by Django 5.2.4 on 2025-07-18 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_userprofile_address_userprofile_date_of_birth_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrator'), ('vendor_manager', 'Vendor Manager'), ('vendor_team', 'Vendor Management Team'), ('customer_manager', 'Customer Manager'), ('customer_team', 'Customer Management Team')], default='customer_team', max_length=30),
        ),
    ]
