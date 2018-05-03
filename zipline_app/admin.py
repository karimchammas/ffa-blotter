from django.contrib import admin

# Register your models here.
from .models.zipline_app.zipline_app import Fill, Order, Account, Asset
from .models.zipline_app.placement import Placement
from .models.zipline_app.custodian import Custodian

#class AssetInline(admin.TabularInline):
#    model = Asset
#    extra = 3

class OrderAdmin(admin.ModelAdmin):
    fieldSets = [
        (None,               {'fields': ['pk', 'order_text', 'asset', 'order_side', 'order_qty_unsigned']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    #inlines = [AssetInline]
    list_display = ('pk', 'order_text', 'pub_date', 'was_published_recently', 'asset', 'order_side', 'order_qty_unsigned')
    list_filter = ['pub_date']
    search_fields = ['id', 'order_text', 'asset__asset_symbol']

#class FillAdmin(admin.ModelAdmin):
#    inlines = [AssetInline]

admin.site.register(Order,OrderAdmin)
admin.site.register(Fill)
admin.site.register(Asset)
admin.site.register(Account)
admin.site.register(Placement)
admin.site.register(Custodian)
