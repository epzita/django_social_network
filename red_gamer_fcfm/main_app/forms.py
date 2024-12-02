from django import forms
from .models import Post, VideoGame, UserFCFM
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'game']  # Campos que el usuario podrá rellenar
        labels = {
            'title': 'Título',
            'content': 'Contenido',
            'game': 'Videojuego',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del Post'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Contenido del Post'}),
            'game': forms.Select(attrs={'class': 'form-control'}),
        }

class UserFCFM_CreationForm(forms.ModelForm):
    """
    Formulario customizado que crea un usuario sin privilegios de superusuario
    Basado en el formulario estandar de creacion de usuario incluido con Django
    """

    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmación', widget=forms.PasswordInput)

    
    class Meta:
        """
        Esta subclase permite sobreescribir elementos de ModelForm
        y sus configuraciones.
        """
        
        model = UserFCFM
        fields = ('username', 'email')
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
        }
        help_texts = {
            'username': 'Requerido. Máximo 150 caracteres. Sólo letras, digitos y @/./+/-/_',
        }
        error_messages = {
            'username': {
                'required': 'Por favor, ingresa un nombre de usuario.',
                'unique': 'Este nombre de usuario ya está en uso.',
            },
            'email': {
                'required': 'Por favor, ingresa un correo electrónico.',
                'invalid': 'El correo electrónico no es válido.',
            }
        }

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        print(super())
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
        return user
    

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = UserFCFM
        fields = ['avatar', 'short_description', 'long_description']
        labels = {
            'avatar': 'Cambiar Avatar',
            'short_description': 'Descripción corta',
            'long_description': 'Descipción completa',
        }
        widgets = {
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'title': 'Visible en la lista de usuarios'}),
            'long_description': forms.Textarea(attrs={'class': 'form-control', 'title': 'Visible en tu perfil'}),
        }