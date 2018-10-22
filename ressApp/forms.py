from django.forms import ModelForm
from .models import Offer, Address, Profile
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django import forms
from ressApp import views


class OfferForm(ModelForm):
    """
    Form für das Angebot

    authors:  Katrin Reder-Zirkelbach, Simon Hoffmann
    """
    BlockedDays = forms.CheckboxSelectMultiple()

    class Meta:
        model = Offer
        fields = ['title', 'subtitle', 'description', 'deposit', 'price', 'category', 'lend_or_gift', 'image', 'BlockedDays']
        labels = {
            'title': 'Titel',
            'subtitle': 'Kurzüberschrift',
            'description': 'Beschreibung',
            'deposit': 'Kaution',
            'price': 'Preis',
            'category': 'Kategorie',
            'lend_or_gift': 'Angebot Verleihen oder Verschenken?',
            'image': 'Bild hinzufügen',
            'BlockedDays': 'Mein Angebot gilt NICHT an folgenden Tagen (falls zutreffend):',
        }
        help_texts = {
            'deposit': '(falls gewünscht)',
            'price': '(falls zutreffend)',
        }


class AddressForm(ModelForm):
    """
    Form für das eintragen der Adresse

    authors: Katrin Reder-Zirkelbach, Simon Hoffmann
    """
    class Meta:
        model = Address
        fields = ['street', 'house_number', 'additional_info', 'city', 'postcode']
        labels = {
            'street': 'Straße',
            'house_number': 'Hausnr.',
            'additional_info': 'Hinterhaus, c/o, etc.',
            'city': 'Ort',
            'postcode': 'PLZ',
        }

    def clean(self):
        if (views.addresstolocation(str(self.cleaned_data.get('city')) + " " + str(self.cleaned_data.get('street')) + " " +  str(self.cleaned_data.get('house_number'))) == None):
            raise forms.ValidationError("Ungültig Adresse")
        return self.cleaned_data


class ProfileForm(ModelForm):
    """
    Form für das Benutzerprofil

    authors: Simon Hoffmann, David Hartmann, Katrin Reder-Zirkelbach
    """
    class Meta:
        model = Profile
        fields = ['einrichtungsname', 'phone', 'image']
        labels= {
            'einrichtungsname': 'Meine Organisation',
            'phone': 'Telefonnummer',
            'image': 'Bild',
            }

#
class ChangeUserForm(UserChangeForm):
    """
    Form zum ändern des Userprofils

    authors: Simon Hoffmann, Katrin Reder-Zirkelbach
    """
    class Meta:
        model = User
        fields = ['username', "first_name", "last_name", "email", 'password']
        labels = {
            'username': 'Benutzername',
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail',
            'password': 'Passwort',
        }


class SignUpForm(UserCreationForm):
    """
    Form zum anlegen eines Nutzers

    authors: David Hartmann, Katrin Reder-Zirkelbach
    """
    first_name = forms.CharField(label="Vorname")
    last_name = forms.CharField(label="Nachname")
    email = forms.EmailField(label="E-Mail")
    einrichtungsname = forms.CharField(label="Ihre Organisation")
    phone = forms.CharField(max_length=15, validators=[RegexValidator(r"^\d{8,15}")], label="Telefonnummer")
    street = forms.CharField(label="Straße")
    house_number = forms.CharField(label="Hausnr.")
    additional_info = forms.CharField(label="Hinterhaus, c/o etc.", required=False)
    city = forms.CharField(label="Ortschaft", help_text="Bitte geben Sie Bamberg oder einen Bamberger Ortsteil an")
    postcode = forms.CharField(validators=[
        RegexValidator(regex='^\d{5}$')], help_text='Bitte geben sie eine fünfstellige PLZ ein', label="PLZ")
    image = forms.ImageField(label="Bild")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "einrichtungsname", "phone", "image", "street",
                  "house_number", "additional_info", "city", "postcode", "password1", "password2")

        labels = {
            "username": "Benutzername",
        }
