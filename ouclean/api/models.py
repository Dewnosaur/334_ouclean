from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    address = models.CharField(max_length=500, blank=True)
    tel = models.CharField(max_length=20, blank=True)

class Product(models.Model):
    name = models.CharField(max_length=20)
    price = models.FloatField()
    stock = models.IntegerField()
    picture = models.URLField(max_length=255, null=True, blank=True, help_text="URL to the product image")
    
    def __str__(self):
        return self.name

class Payment(models.Model):
    payment_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.payment_owner.username}'s payment - {self.method}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    total_price = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, related_name='orders')
    shipping_address = models.CharField(max_length=500)  # Added shipping_address field
    created_at = models.DateTimeField(auto_now_add=True)  # Additional field to track order creation
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_orders')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='product_orders')
    quantity = models.IntegerField()
    total_price = models.FloatField()
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"