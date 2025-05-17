from django.db import models
from django.contrib.auth.models import User

# Constants
COURSE_LEVELS = (
    ('Beginner', 'Beginner'),
    ('Advanced', 'Advanced'),
    ('Professional', 'Professional'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorites = models.ManyToManyField('Course', blank=True, related_name='favorited_by')

    def __str__(self):
        return self.user.username

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_days = models.PositiveIntegerField()
    level = models.CharField(max_length=20, choices=COURSE_LEVELS)
    location = models.CharField(max_length=250, null=True, blank=True)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    
    # Static requirement fields
    min_age = models.CharField(max_length=10)
    required_time = models.CharField(max_length=100)
    max_depth = models.CharField(max_length=100)
    health_notes = models.TextField()

    def __str__(self):
        return self.title
  
class CourseFeature(models.Model):
    course = models.ForeignKey(Course, related_name='features', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.course_id} - {self.course.title} | {self.description}'


class CourseLearningPoint(models.Model):
    course = models.ForeignKey(Course, related_name='learning_points', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.course_id} - {self.course.title} | {self.description}'

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField()
    review = models.TextField(blank=True)

    
    def __str__(self):
        return f'{self.user.username} - {self.course.title} | {self.rating}'


# Shop Products
class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.title

# Cart / Checkout
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if (self.course):
            return f'{self.user.username} - {self.course.title}'
        elif(self.product):
            return f'{self.user.username} - {self.product.title}'


    def get_total_price(self):
        """Calculate the total price of the cart item based on the product or course."""
        if self.course:
            return self.course.price * self.quantity
        elif self.product:
            return self.product.price * self.quantity
        return 0




class Order(models.Model):
    PAYMENT_CHOICES=(
        ('cash', 'Cash'),
        ('visa', 'Visa'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')

    
    def __str__(self):
        return f'{self.user.username} - {self.created_at} | {self.total_price} L.E.'
