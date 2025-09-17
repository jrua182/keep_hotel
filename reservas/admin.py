from django.contrib import admin
from .models import Activity, Schedule, Room, Reservation

admin.site.register(Activity)
admin.site.register(Schedule)
admin.site.register(Room)
admin.site.register(Reservation)
