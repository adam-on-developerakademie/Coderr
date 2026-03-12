from django.contrib import admin
from offers_app.models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    model = OfferDetail
    extra = 0
    readonly_fields = ['offer_type']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'min_price', 'min_delivery_time', 'created_at']
    list_filter = ['created_at', 'updated_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'min_price', 'min_delivery_time']
    inlines = [OfferDetailInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'image', 'description')
        }),
        ('Berechnete Felder', {
            'fields': ('min_price', 'min_delivery_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ['get_offer_title', 'offer_type', 'price', 'delivery_time_in_days', 'revisions']
    list_filter = ['offer_type', 'offer__created_at']
    search_fields = ['title', 'offer__title', 'offer__user__username']
    ordering = ['offer__title', 'offer_type']
    
    def get_offer_title(self, obj):
        return obj.offer.title
    get_offer_title.short_description = 'Angebot'
