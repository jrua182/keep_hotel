from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Activity, Schedule, Reservation, Room, RoomType
from .forms import ReservationForm, RoomSearchForm

def index(request):
    """Página principal del hotel"""
    activities = Activity.objects.filter(is_active=True)[:6]  # Mostrar solo 6 actividades
    room_types = RoomType.objects.all()[:3]  # Mostrar 3 tipos de habitación
    
    context = {
        'activities': activities,
        'room_types': room_types,
        'today': timezone.now().date(),
    }
    return render(request, 'reservas/index.html', context)

def activities_list(request):
    """Lista completa de actividades"""
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    activities = Activity.objects.filter(is_active=True)
    
    if category:
        activities = activities.filter(category=category)
    
    if search:
        activities = activities.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    categories = Activity.CATEGORY_CHOICES
    
    context = {
        'activities': activities,
        'categories': categories,
        'current_category': category,
        'search_query': search,
    }
    return render(request, 'reservas/activities_list.html', context)

def activity_detail(request, activity_id):
    """Detalle de una actividad específica"""
    activity = get_object_or_404(Activity, pk=activity_id, is_active=True)
    
    # Obtener horarios disponibles (próximos 30 días)
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=30)
    
    schedules = Schedule.objects.filter(
        activity=activity,
        date__range=[start_date, end_date],
        available_spots__gt=0
    ).order_by('date', 'start_time')
    
    context = {
        'activity': activity,
        'schedules': schedules,
    }
    return render(request, 'reservas/activity_detail.html', context)

def rooms_list(request):
    """Lista de habitaciones disponibles"""
    form = RoomSearchForm(request.GET)
    rooms = []
    
    if form.is_valid():
        check_in = form.cleaned_data.get('check_in')
        check_out = form.cleaned_data.get('check_out')
        guests = form.cleaned_data.get('guests')
        
        if check_in and check_out:
            # Buscar habitaciones disponibles
            occupied_rooms = Reservation.objects.filter(
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=['confirmed', 'pending']
            ).values_list('room_id', flat=True)
            
            available_rooms = Room.objects.filter(
                is_available=True,
                room_type__max_capacity__gte=guests or 1
            ).exclude(id__in=occupied_rooms)
            
            rooms = available_rooms
    
    room_types = RoomType.objects.all()
    
    context = {
        'form': form,
        'rooms': rooms,
        'room_types': room_types,
    }
    return render(request, 'reservas/rooms_list.html', context)

def reserve_activity(request, schedule_id):
    """Reservar una actividad"""
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    
    if schedule.available_spots <= 0:
        messages.error(request, 'No hay cupos disponibles para este horario.')
        return redirect('activity_detail', activity_id=schedule.activity.id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.activity = schedule.activity
            reservation.schedule = schedule
            reservation.total_price = schedule.activity.price
            reservation.save()
            
            # Reducir cupos disponibles
            schedule.available_spots -= 1
            schedule.save()
            
            # Enviar email de confirmación
            send_confirmation_email(reservation)
            
            messages.success(request, '¡Reserva confirmada exitosamente!')
            return redirect('reservation_confirmation', reservation_id=reservation.id)
    else:
        form = ReservationForm()
    
    context = {
        'form': form,
        'schedule': schedule,
        'activity': schedule.activity,
    }
    return render(request, 'reservas/reserve_activity.html', context)

def reserve_room(request, room_id):
    """Reservar una habitación"""
    room = get_object_or_404(Room, pk=room_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.room = room
            
            # Calcular precio total
            check_in = reservation.check_in
            check_out = reservation.check_out
            nights = (check_out - check_in).days
            reservation.total_price = room.room_type.price_per_night * nights
            
            reservation.save()
            
            # Enviar email de confirmación
            send_confirmation_email(reservation)
            
            messages.success(request, '¡Reserva de habitación confirmada!')
            return redirect('reservation_confirmation', reservation_id=reservation.id)
    else:
        # Pre-llenar fechas si vienen por GET
        initial_data = {}
        if request.GET.get('check_in'):
            initial_data['check_in'] = request.GET.get('check_in')
        if request.GET.get('check_out'):
            initial_data['check_out'] = request.GET.get('check_out')
        if request.GET.get('guests'):
            initial_data['guests_count'] = request.GET.get('guests')
            
        form = ReservationForm(initial=initial_data)
    
    context = {
        'form': form,
        'room': room,
    }
    return render(request, 'reservas/reserve_room.html', context)

def reservation_confirmation(request, reservation_id):
    """Página de confirmación de reserva"""
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    
    context = {
        'reservation': reservation,
    }
    return render(request, 'reservas/confirmation.html', context)

def send_confirmation_email(reservation):
    """Enviar email de confirmación"""
    subject = f'Confirmación de reserva - Hotel Paradise'
    
    if reservation.room:
        message = f"""
        Estimado/a {reservation.guest_name},
        
        Su reserva de habitación ha sido confirmada:
        
        Habitación: {reservation.room}
        Check-in: {reservation.check_in}
        Check-out: {reservation.check_out}
        Huéspedes: {reservation.guests_count}
        Total: ${reservation.total_price}
        
        ¡Esperamos su visita!
        """
    else:
        message = f"""
        Estimado/a {reservation.guest_name},
        
        Su reserva de actividad ha sido confirmada:
        
        Actividad: {reservation.activity.name}
        Fecha: {reservation.schedule.date}
        Hora: {reservation.schedule.start_time} - {reservation.schedule.end_time}
        Total: ${reservation.total_price}
        
        ¡Nos vemos pronto!
        """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [reservation.guest_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error enviando email: {e}")