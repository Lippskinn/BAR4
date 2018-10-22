from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from multiselectfield import MultiSelectField

# Hilfsvariable; authors (für alle Choices): Katrin Reder-Zirkelbach
CATEGORY_CHOICES = (
    ('RO', "Räume"),
    ('TO', "Werkzeug"),
    ('EV', "Eventequipment"),
    ('EL', "Elektronik"),
    ('OF', "Büroausstattung"),
    ('TR', "Transportmittel"),
    ('HO', "Küchengeräte"),
    ('SP', "Sport & Spiel"),
    ('ME', "Medien"),
    ('SE', "Dienstleistungen und Wissen"),
    ('OT', "Sonstiges"),
)

# Hilfsvariable;
DAYS_OF_WEEK = {
    (0, 'Montag'),
    (1, 'Dienstag'),
    (2, 'Mittwoch'),
    (3, 'Donnerstag'),
    (4, 'Freitag'),
    (5, 'Samstag'),
    (6, 'Sonntag'),
}

# Hilfsvariable;
LEND_OR_GIFT_CHOICES = (
    ('VL', 'Verleihen'),
    ('VS', 'Verschenken'),
)


class Address(models.Model):
    """
    Adressklasse

    authors: Katrin Reder-Zirkelbach
    """
    street = models.CharField(max_length=200)
    house_number = models.CharField(max_length=5)
    additional_info = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=100)
    #CharField für postcode, weil integerfield kein max_length erkennt
    postcode = models.CharField(max_length=5, validators=[RegexValidator(regex='^\d{5}$', message='Bitte geben sie eine fünfstellige PLZ ein')])
    latitude = models.FloatField(default=49.89873) #Default is Bamberg
    longitude = models.FloatField(default=10.90067) #Default is Bamberg


class Offer(models.Model):
    """
    Offer Klasse

    authors: Katrin Reder-Zirkelbach, Julian Sears
    """
    # Titel/Überschrift
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, default="")
    # enthält auch "besondere Nutzungsbedingungen" (Spezifikation)
    description = models.TextField(max_length=600)
    created_at = datetime.now
    # if the adress is deleted, the respective field in the offer table will be set to null
    offerAdress= models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    deposit = models.IntegerField(default=0, null=True)
    price = models.IntegerField(default=0, null=True)
    #1 is the super user's ID
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    BlockedDays = MultiSelectField(choices=DAYS_OF_WEEK, null=True, blank=True)

    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True,
        default='OT',
    )

    lend_or_gift = models.CharField(
        max_length=2,
        choices=LEND_OR_GIFT_CHOICES,
        default='VL',
    )
    image = models.ImageField(upload_to="offer_image", default="offer_image/no_offer_image.jpg")


class Profile(models.Model):
    """
    Userprofil

    authors: David Hartmann, Julian Sears
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    einrichtungsname = models.CharField(max_length=50, null=True)
    address = models.ForeignKey("Address", on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=15, validators=[RegexValidator(r"^\d{8,15}", message="Geben Sie eine valide Telefonnummer ein (8 bis 15 Ziffern)")], null=True)
    image = models.ImageField(upload_to="profile_image", default="profile_image/no_profile_image.jpg")

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    """
    Methode um Userprofil richtig anzulegen

    authors: David Hartmann
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
