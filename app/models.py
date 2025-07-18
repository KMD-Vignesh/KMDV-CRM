from django.contrib.auth.models import User
from django.db import models
from django.db.models import F   # add to model imports if not already present

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    vendor_id = models.CharField(max_length=20,unique=True, verbose_name="Vendor ID")  
    name      = models.CharField(max_length=100)
    address   = models.TextField()

    def __str__(self):
        return f"{self.vendor_id} – {self.name}"


class Product(models.Model):
    product_id = models.CharField(max_length=20, unique=True, verbose_name="Product ID")
    name       = models.CharField(max_length=100)
    category   = models.ForeignKey(Category, on_delete=models.CASCADE)
    price      = models.DecimalField(max_digits=10, decimal_places=2)
    description= models.TextField(blank=True)

    def __str__(self):
        return f"{self.product_id} – {self.name}"


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    inward_qty     = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.product.name} - {self.stock_quantity}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        if self.pk and self.is_cancelled:
            original_order = Order.objects.filter(pk=self.pk).first()
            if original_order and not original_order.is_cancelled:
                # Restore stock to every matching Inventory row (FIFO-style)
                remaining = self.quantity
                for inv in (
                    Inventory.objects
                    .filter(product=self.product, vendor=self.vendor)
                    .order_by('id')
                ):
                    add = min(remaining, inv.stock_quantity + remaining)  # always safe
                    inv.stock_quantity = F('stock_quantity') + add
                    inv.save(update_fields=['stock_quantity'])
                    remaining -= add
                    if remaining == 0:
                        break

        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ROLE_CHOICES = [
        ('admin',           'Administrator'),
        ('vendor_manager',   'Vendor Manager'),
        ('vendor_team',      'Vendor Management Team'),
        ('customer_manager', 'Customer Manager'),
        ('customer_team',    'Customer Management Team'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='customer_team')

    date_of_birth = models.DateField(null=True, blank=True)
    date_of_join  = models.DateField(null=True, blank=True)
    designation   = models.CharField(max_length=100, blank=True)
    work_location = models.CharField(max_length=100, blank=True)
    address       = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} – {self.get_role_display()}"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('PO_RAISED',  'PO Raised'),
        ('PO_APPROVED','PO Approved'),
        ('SHIPPED',    'Shipped'),
        ('DELIVERED',  'Delivered'),
        ('INWARD_DONE','Inward Done'),
    ]

    product         = models.ForeignKey('Product', on_delete=models.CASCADE)
    vendor          = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    quantity        = models.PositiveIntegerField()
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PO_RAISED')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO #{self.pk} — {self.product.name} ({self.quantity})"