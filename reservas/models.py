from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class RoomType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_capacity = models.IntegerField()
    amenities = models.TextField(help_text="Separar amenidades con comas")
    
    def __str__(self):
        return self.name

class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    floor = models.IntegerField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['number']
    
    def __str__(self):
        return f"Habitación {self.number} - {self.room_type.name}"

class Activity(models.Model):
    CATEGORY_CHOICES = [
        ('spa', 'Spa & Wellness'),
        ('sport', 'Deportes'),
        ('entertainment', 'Entretenimiento'),
        ('dining', 'Restaurante'),
        ('other', 'Otros'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_hours = models.IntegerField(default=1)
    max_participants = models.IntegerField(default=10)
    image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Activities"
    
    def __str__(self):
        return self.name

class Schedule(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    available_spots = models.IntegerField()
    
    class Meta:
        unique_together = ['activity', 'date', 'start_time']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.activity.name} - {self.date} {self.start_time}-{self.end_time}"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
    ]
    
    # Información del huésped
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20, blank=True)
    
    # Reserva de habitación
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    guests_count = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Reserva de actividad
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True, blank=True)
    
    # Estado y metadatos
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.room:
            return f"Reserva habitación {self.room.number} - {self.guest_name}"
        elif self.activity:
            return f"Reserva {self.activity.name} - {self.guest_name}"
        return f"Reserva - {self.guest_name}"