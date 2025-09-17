from django import forms
from django.utils import timezone
from datetime import date, timedelta
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'guest_name', 'guest_email', 'guest_phone',
            'check_in', 'check_out', 'guests_count', 
            'special_requests'
        ]
        widgets = {
            'guest_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'guest_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'guest_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'check_in': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'check_out': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': (date.today() + timedelta(days=1)).isoformat()
            }),
            'guests_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Solicitudes especiales (opcional)'
            }),
        }
        labels = {
            'guest_name': 'Nombre completo',
            'guest_email': 'Correo electrónico',
            'guest_phone': 'Teléfono',
            'check_in': 'Fecha de entrada',
            'check_out': 'Fecha de salida',
            'guests_count': 'Número de huéspedes',
            'special_requests': 'Solicitudes especiales',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise forms.ValidationError(
                    'La fecha de salida debe ser posterior a la fecha de entrada.'
                )
            
            if check_in < date.today():
                raise forms.ValidationError(
                    'La fecha de entrada no puede ser anterior a hoy.'
                )
        
        return cleaned_data

class RoomSearchForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        }),
        label='Fecha de entrada',
        initial=date.today()
    )
    
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': (date.today() + timedelta(days=1)).isoformat()
        }),
        label='Fecha de salida',
        initial=date.today() + timedelta(days=1)
    )
    
    guests = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 10
        }),
        label='Huéspedes',
        initial=1,
        min_value=1,
        max_value=10
    )