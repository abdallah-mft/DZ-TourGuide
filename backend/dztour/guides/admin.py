from django.contrib import admin
from .models import Language, Wilaya, Commune, GuideProfile, Certifications


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['name', 'code']


@admin.register(Wilaya)
class WilayaAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_fr', 'name_ar']
    search_fields = ['name_fr', 'name_ar', 'code']


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_fr', 'wilaya']
    list_filter = ['wilaya']
    search_fields = ['name_fr', 'name_ar', 'code']


@admin.register(GuideProfile)
class GuideProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'phone_number', 'created_at']
    list_filter = ['is_verified', 'wilaya_covered']
    search_fields = ['user__email', 'bio']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Certifications)
class CertificationsAdmin(admin.ModelAdmin):
    list_display = ['name', 'guide_profile']
    search_fields = ['name']
