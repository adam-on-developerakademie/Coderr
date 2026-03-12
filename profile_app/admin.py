from django.contrib import admin
from profile_app.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = [
		'id',
		'user',
		'first_name',
		'last_name',
		'type',
		'location',
		'uploaded_at',
	]
	list_filter = ['type', 'uploaded_at', 'created_at']
	search_fields = ['user__username', 'first_name', 'last_name', 'location', 'tel']
	readonly_fields = ['uploaded_at', 'created_at']
	ordering = ['-created_at']
