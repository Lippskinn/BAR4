from django.contrib import admin
from .models import Offer, Address, Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

"""
Kofigurationen für die Admin-Site

authors: David Hartmann,
"""

admin.site.register(Offer)
admin.site.register(Address)
admin.site.register(Profile)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)