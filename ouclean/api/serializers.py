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
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'address', 'tel']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError("Passwords don't match.")
        return data
    
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
        fields = ['id', 'name', 'price', 'stock', 'picture']

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
    products = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = ['customer', 'shipping_address', 'payment', 'products']
    
    def create(self, validated_data):
        products_data = validated_data.pop('products')
        
        # Calculate total order price
        total_price = 0
        
        # Create order
        order = Order.objects.create(
            customer=validated_data['customer'],
            shipping_address=validated_data['shipping_address'],
            payment=validated_data.get('payment'),
            total_price=0,  # Will update after calculating from product orders
            status='pending'
        )
        
        # Create product orders
        for product_item in products_data:
            product = Product.objects.get(id=product_item['product_id'])
            quantity = product_item['quantity']
            
            if quantity > product.stock:
                raise serializers.ValidationError(f"Not enough stock for {product.name}")
            
            item_total = product.price * quantity
            total_price += item_total
            
            ProductOrder.objects.create(
                product=product,
                order=order,
                quantity=quantity,
                total_price=item_total
            )
            
            # Update stock
            product.stock -= quantity
            product.save()
        
        # Update order total price
        order.total_price = total_price
        order.save()
        
        return order