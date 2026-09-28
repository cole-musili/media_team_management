from django.contrib import admin
from .models import EquipmentCategory, Equipment, EquipmentPhoto, Checkout, MaintenanceRecord

admin.site.register(EquipmentCategory)
admin.site.register(Equipment)
admin.site.register(EquipmentPhoto)
admin.site.register(Checkout)
admin.site.register(MaintenanceRecord)
