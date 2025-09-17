from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Actividades
    path('actividades/', views.activities_list, name='activities_list'),
    path('actividad/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('reservar-actividad/<int:schedule_id>/', views.reserve_activity, name='reserve_activity'),
    
    # Habitaciones
    path('habitaciones/', views.rooms_list, name='rooms_list'),
    path('reservar-habitacion/<int:room_id>/', views.reserve_room, name='reserve_room'),
    
    # Confirmaciones
    path('confirmacion/<int:reservation_id>/', views.reservation_confirmation, name='reservation_confirmation'),
]