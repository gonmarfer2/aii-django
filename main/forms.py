#encoding:utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
   
class UsuarioBusquedaForm(forms.Form):
    idUsuario = forms.IntegerField(label="Id de Usuario", widget=forms.TextInput(attrs={
        "autofocus": True,
        "class":"form-control"
    }), required=True)
    
class PeliculaBusquedaYearForm(forms.Form):
    year = forms.IntegerField(label="Año de publicación", widget=forms.TextInput(attrs={
        "autofocus": True,
        "class":"form-control"
    }), required=True)

class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        "autofocus": True,
        "class": "form-control"
        }))
    password = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "class": "form-control"
            }),
    )