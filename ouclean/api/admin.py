from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Order, ProductOrder, Payment

# User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'tel')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('address', 'tel')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('address', 'tel')}),
    )

admin.site.register(User, CustomUserAdmin)

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock')
    search_fields = ('name',)
    list_filter = ('stock',)

# Product Order Inline
class ProductOrderInline(admin.TabularInline):
    model = ProductOrder
    extra = 1
    readonly_fields = ('total_price',)

# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username',)
    inlines = [ProductOrderInline]
    readonly_fields = ('total_price',)

# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_owner', 'method')
    search_fields = ('payment_owner__username',)