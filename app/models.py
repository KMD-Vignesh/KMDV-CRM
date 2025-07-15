from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)

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
        # Only handle stock changes for new orders or cancellations
        # Stock reduction will be handled in the view for better error handling
        if self.pk and self.is_cancelled:
            # Handle cancellation - restore stock
            try:
                original_order = Order.objects.get(pk=self.pk)
                if (
                    not original_order.is_cancelled
                ):  # Only restore if not already cancelled
                    inventory = Inventory.objects.get(
                        product=self.product, vendor=self.vendor
                    )
                    inventory.stock_quantity += self.quantity
                    inventory.save()
            except (Order.DoesNotExist, Inventory.DoesNotExist):
                pass  # Handle gracefully if inventory doesn't exist

        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50,
        choices=[("admin", "Admin"), ("staff", "Staff"), ("viewer", "Viewer")],
    )
    permissions = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
