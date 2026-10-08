from django.contrib import admin
from .models import Crop, Plot, HarvestSchedule, HarvestRecord

admin.site.register(Crop)
admin.site.register(Plot)
admin.site.register(HarvestSchedule)
admin.site.register(HarvestRecord)
