from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, action
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        # token['groups'] = user.groups.all()
        token['username'] = user.username
        token['profile'] = user.profile.id
        
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Sign up
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Account Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    # Return users based on roles
    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)  # users see only themselves
        
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
    @api_view(['POST'])
    def add_to_cart(request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        course = Course.objects.get(id=data.get("course_id")) if data.get("course_id") else None
        product = Product.objects.get(id=data.get("product_id")) if data.get("product_id") else None

        # Check if item is already in the cart
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            course=course,
            product=product,
            defaults={'quantity': data.get('quantity', 1)}
        )
        
        if not created:
            # Update quantity if the item already exists in cart
            cart_item.quantity += data.get('quantity', 1)
            cart_item.save()

        return Response({"detail": "Item added to cart successfully!"}, status=status.HTTP_201_CREATED)

    @api_view(['POST'])
    def checkout(request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        cart_items_data = request.data.get('cart_items', [])

        if not cart_items_data:
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        cart_items_created = []

        order = Order.objects.create(user=request.user)

        for item in cart_items_data:
            quantity = item.get("quantity", 1)

            course = None
            product = None

            # Handle course-based items
            course_id = item.get("course_id") or item.get("id")  # Fallback to id if needed
            if item.get("type") == "course" or "course_id" in item or "title" in item:
                try:
                    course = Course.objects.get(id=course_id)
                    total_price += course.price * quantity
                    cart_item = CartItem.objects.create(
                        user=request.user,
                        course=course,
                        quantity=quantity
                    )
                    cart_items_created.append(cart_item)
                    continue
                except Course.DoesNotExist:
                    pass  # or return error

            # Handle product-based items
            product_id = item.get("product_id") or item.get("id")
            if item.get("type") == "product" or "product_id" in item:
                try:
                    product = Product.objects.get(id=product_id)
                    total_price += product.price * quantity
                    cart_item = CartItem.objects.create(
                        user=request.user,
                        product=product,
                        quantity=quantity
                    )
                    cart_items_created.append(cart_item)
                    continue
                except Product.DoesNotExist:
                    pass  # or return error

        # Associate items with the order
        order.items.set(cart_items_created)
        order.total_price = total_price
        order.save()

        return Response({"detail": "Order placed successfully!"}, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
            order = serializer.save(user=self.request.user)
            # cart_items = []
            # Save CartItems and link them to the order
            cart_items = self.request.data.get('cart_items', [])
            for item in cart_items:
                course_id = item.get('course_id')
                product_id = item.get('product_id')
                quantity = item.get('quantity')

                # Save CartItem and associate it with the order
                if course_id:
                    course = Course.objects.get(id=course_id)
                    cart_item = CartItem.objects.create(
                        user=self.request.user,
                        course=course,
                        quantity=quantity
                    )
                elif product_id:
                    product = Product.objects.get(id=product_id)
                    cart_item = CartItem.objects.create(
                        user=self.request.user,
                        product=product,
                        quantity=quantity
                    )

                # Link CartItem to the order
                order.items.add(cart_item)

            # Set the total price of the order
            total_price = sum([item['quantity'] * (Course.objects.get(id=item.get('course_id')).price if item.get('course_id') else Product.objects.get(id=item.get('product_id')).price) for item in cart_items])
            order.total_price = total_price
            order.save()
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = self.get_queryset().get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request, pk=None):
        profile = self.get_queryset().get(user=request.user)
        course = get_object_or_404(Course, pk=pk)

        if course in profile.favorites.all():
            profile.favorites.remove(course)
            return Response({'status': 'removed'})
        else:
            profile.favorites.add(course)
            return Response({'status': 'added'})

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all() 
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
