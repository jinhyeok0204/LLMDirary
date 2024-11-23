from django.contrib import admin

from .models import Person, User, Counselor, CustomerSupport


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('login_id', 'name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('login_id', 'name', 'role')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'gender', 'birth')


@admin.register(Counselor)
class CounselorAdmin(admin.ModelAdmin):
    list_display = ('id', 'gender')


@admin.register(CustomerSupport)
class CustomerSupportAdmin(admin.ModelAdmin):
    list_display = ('id', 'salary')