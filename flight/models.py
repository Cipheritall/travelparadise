from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import datetime

# Create your models here.

class User(AbstractUser):
    def __str__(self):
        return f"{self.id}: {self.first_name} {self.last_name}"

class Place(models.Model):
    city = models.CharField(max_length=64)
    airport = models.CharField(max_length=64)
    code = models.CharField(max_length=3)
    country = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.city}, {self.country} ({self.code})"


class Week(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.name} ({self.number})"


class Segment(models.Model):
    link =  models.CharField(max_length=255,default=None)
    id = models.IntegerField(primary_key=True)
    departure = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="seg_departures")
    departure_date = models.DateField(auto_now=False, auto_now_add=False,default=None)
    departure_time = models.TimeField(auto_now=False, auto_now_add=False,default=None)
    arrival =  models.ForeignKey(Place, on_delete=models.CASCADE, related_name="seg_arrivals")
    arrival_date =  models.DateField(auto_now=False, auto_now_add=False,default=None)
    arrival_time = models.TimeField(auto_now=False, auto_now_add=False,default=None)
    mk_carrier_code = models.CharField(max_length=64,default=None)
    op_carrier_code =models.CharField(max_length=64,default=None)
    numberOfStops =models.CharField(max_length=64,default=None)
    duration = models.CharField(max_length=64,default=None)
    aircraft = models.CharField(max_length=64,default=None)
    
    def __str__(self):
        return f"{self.id}: {self.departure} to {self.arrival}"
    
class Flight(models.Model):
    id = models.IntegerField(primary_key=True)
    link = models.CharField(max_length=255,default=None)
    origin = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="departures",default=None)
    destination = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="arrivals",default=None)
    depart_time = models.TimeField(auto_now=False, auto_now_add=False,default=None,null=True)
    departure_date = models.DateField(auto_now=False, auto_now_add=False,default=None)
    duration = models.DurationField(default=None,null=True)
    arrival_date =  models.DateField(auto_now=False, auto_now_add=False,default=None)
    arrival_time = models.TimeField(auto_now=False, auto_now_add=False,default=None,null=True)
    plane = models.CharField(max_length=24,default=None,null=True)
    airline = models.CharField(max_length=64,default=None,null=True)
    price_grand_total = models.FloatField(null=True,default=None)
    price_base = models.FloatField(null=True,default=None)
    price_currency = models.CharField(max_length=64,default=None,null=True)
    fare_type = models.CharField(max_length=64,default=None,null=True)
    segments = models.ManyToManyField(Segment,default=None)

    def __str__(self):
        return f"{self.id}: {self.origin} to {self.destination}"



GENDER = (
    ('male','MALE'),    #(actual_value, human_readable_value)
    ('female','FEMALE')
)

class Passenger(models.Model):
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER, blank=True)
    #passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name="flights")
    #flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="passengers")

    def __str__(self):
        return f"Passenger: {self.first_name} {self.last_name}, {self.gender}"



SEAT_CLASS = (
    ('economy', 'Economy'),
    ('business', 'Business'),
    ('first', 'First')
)

TICKET_STATUS =(
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('CANCELLED', 'Cancelled')
)

class Ticket(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="bookings", blank=True, null=True)
    ref_no = models.CharField(max_length=6, unique=True)
    passengers = models.ManyToManyField(Passenger, related_name="flight_tickets")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets", blank=True, null=True)
    flight_ddate = models.DateField(blank=True, null=True)
    flight_adate = models.DateField(blank=True, null=True)
    flight_fare = models.FloatField(blank=True,null=True)
    other_charges = models.FloatField(blank=True,null=True)
    coupon_used = models.CharField(max_length=15,blank=True)
    coupon_discount = models.FloatField(default=0.0)
    total_fare = models.FloatField(blank=True, null=True)
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS)
    booking_date = models.DateTimeField(default=datetime.now)
    mobile = models.CharField(max_length=20,blank=True)
    email = models.EmailField(max_length=45, blank=True)
    status = models.CharField(max_length=45, choices=TICKET_STATUS)

    def __str__(self):
        return self.ref_no