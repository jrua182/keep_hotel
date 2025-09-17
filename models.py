class Activity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class Schedule(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

class Room(models.Model):
    number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)

class Reservation(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    status = models.CharField(max_length=20, default='Pending')
    reservation_date = models.DateTimeField(auto_now_add=True)
