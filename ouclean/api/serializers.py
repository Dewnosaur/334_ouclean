from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Product, Order, ProductOrder, Payment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'address', 'tel']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'}, required=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("ไม่สามารถเข้าสู่ระบบได้ กรุณาตรวจสอบอีเมลและรหัสผ่าน")
        else:
            raise serializers.ValidationError("กรุณาระบุอีเมลและรหัสผ่าน")

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'address', 'tel']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            address=validated_data.get('address', ''),
            tel=validated_data.get('tel', '')
        )
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'picture', 'description','stock']  # add 'description'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_owner', 'method']

class ProductOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = ProductOrder
        fields = ['id', 'product', 'product_name', 'quantity', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    product_orders = ProductOrderSerializer(many=True, read_only=True)
    customer_username = serializers.ReadOnlyField(source='customer.username')
    
    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'customer', 'customer_username', 
                  'payment', 'shipping_address', 'created_at', 'product_orders']
        read_only_fields = ['total_price']  # Total price is calculated from product orders

class OrderCreateSerializer(serializers.ModelSerializer):
    products = serializers.ListField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'payment', 'shipping_address', 'products', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for prod in products_data:
            # Look up product by name
            try:
                product = Product.objects.get(name=prod['name'])
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product '{prod['name']}' does not exist.")
            ProductOrder.objects.create(
                order=order,
                product=product,
                quantity=prod['quantity'],
                total_price=prod.get('total_price', 0)
            )
        return order