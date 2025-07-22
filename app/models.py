from django.contrib.auth.models import User
from django.db import models
from django.db.models import F


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    vendor_id = models.CharField(max_length=20, unique=True, verbose_name="Vendor ID")
    name = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return f"{self.vendor_id} – {self.name}"


class Product(models.Model):
    product_id = models.CharField(max_length=20, unique=True, verbose_name="Product ID")
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product_id} – {self.name}"


class Inventory(models.Model):
    STATUS_CHOICES = [
        ("INWARD_REQUESTED", "Requested"),
        ("INWARD_APPROVED", "Approved"),
        ("INWARD_REJECTED", "Rejected"),
        ("INWARD_COMPLETED", "Completed"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField()
    inward_qty = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="INWARD_REQUESTED"
    )
    last_updated = models.DateTimeField(auto_now=True)
    inward_date = models.DateTimeField(auto_now_add=True) 
    approval_status = models.CharField(
            max_length=20,
            choices=[
                ('PENDING',  'Pending'),
                ('APPROVED', 'Approved'),
                ('CANCELLED','Cancelled'),
            ],
            default='PENDING'
        )
    def __str__(self):
        return (
            f"{self.product.name} - {self.stock_quantity} ({self.get_status_display()})"
        )


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
            ('ORDER_RAISED',  'Raised'),
            ('ORDER_APPROVED','Approved'),
            ('ORDER_REJECTED','Rejected'),
            ('ORDER_SHIPPED', 'Shipped'),
            ('ORDER_DELIVERED','Delivered'),
            ('ORDER_RETURNED','Returned'),
        ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ORDER_RAISED'
    )

    APPROVAL_CHOICES = [
        ('PENDING',   'Pending'),
        ('APPROVED',  'Approved'),
        ('CANCELLED', 'Cancelled'),
    ]
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default='PENDING'
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("sourcing_team", "Sourcing Team"),
        ("sourcing_manager", "Sourcing Manager"),
        ("sales_team", "Sales Team"),
        ("sales_manager", "Sales Manager"),
        ("logistics_team", "Logistics Team"),
        ("logistics_manager", "Logistics Manager"),
        ("team_lead", "Team Leader"),


    ]
    role = models.CharField(
        max_length=30, choices=ROLE_CHOICES, default="customer_team"
    )

    date_of_birth = models.DateField(null=True, blank=True)
    date_of_join = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    work_location = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    employee_id = models.CharField(max_length=50, unique=True, blank=True, editable=False)

    def __str__(self):
        return f"{self.user.username} – {self.get_role_display()}"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('PO_RAISED',  'Raised'),
        ('PO_APPROVED','Approved'),
        ('PO_REJECTED','Rejected'),
        ('PO_SHIPPED',    'Shipped'),
        ('PO_DELIVERED',  'Delivered'),
        ('INWARD_REQUESTED','Inward'),
    ]
    APPROVAL_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
    ]

    product         = models.ForeignKey('Product', on_delete=models.CASCADE)
    vendor          = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    quantity        = models.PositiveIntegerField()
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PO_RAISED')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='PENDING')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO #{self.pk} — {self.product.name} ({self.quantity})"
