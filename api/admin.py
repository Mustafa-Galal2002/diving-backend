from django.contrib import admin
from .models import (
    Course, CourseFeature, CourseLearningPoint, Rating,
    Product, CartItem, Order, UserProfile
)

class CourseFeatureInline(admin.TabularInline):
    model = CourseFeature
    extra = 1

class CourseLearningPointInline(admin.TabularInline):
    model = CourseLearningPoint
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseFeatureInline, CourseLearningPointInline]
    list_display = ('title', 'level', 'price', 'number_of_days')
    search_fields = ('title',)
    list_filter = ('level',)

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseFeature)
admin.site.register(CourseLearningPoint)
admin.site.register(Rating)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(UserProfile)
