from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.http import urlquote

# AbstractUser ya trae username y password, que son obligatorios.
# además, trae opcionalmente first_name, last_name e email,
# que probablemente no vamos a usar.

# Modelo de datos que representa una entrada para un videojuego
# Se debe definir videojuego antes de usuario, sino arroja advertencia
class VideoGame(models.Model):
    name = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to ='logos/', blank=True)
    
    @property
    def url_name(self):
        """una version percent-encoded del nombre, para usarlo en urls"""
        return urlquote(self.name)
    
    @property
    def url(self):
        """da la parte de path de la url correspondiente a este juego"""
        return f'/game/{urlquote(self.name)}'
    
    @property
    def follow_count(self):
        """da la cantidad de usuarios que siguen este juego"""
        return self.followed_by.count()
    
    @property
    def logo_url(self):
        """da la url del logo, si tiene, o uno por defecto"""
        if self.logo:
            return f'/media/{self.logo}'
        return '/static/assets/default_avatar.png'

    def __str__(self):
        return self.name
    

    
# Las otras relaciones (autor de un post, like a post) van en los otros modelos
class UserFCFM(AbstractUser):
    avatar = models.ImageField(upload_to ='avatar/', blank=True)
    long_description = models.CharField(max_length=500, blank=True)
    short_description = models.CharField(max_length=50, blank=True)
    followed_games = models.ManyToManyField(VideoGame, related_name='followed_by', blank=True)
    liked_posts = models.ManyToManyField('Post', related_name = 'liked_by', blank=True)
    #el Post esta con comillas para indicar a Django que busque despues la clase, pues post esta definida despues

    @property
    def avatar_url(self):
        """da la url del avatar, si tiene, o uno por defecto"""
        if self.avatar:
            return f'/media/{self.avatar}'
        return '/static/assets/default_avatar.png'

    @property
    def url_name(self):
        """una version percent-encoded del username, para usarlo en urls"""
        return urlquote(self.username)

    @property
    def user_url(self):
        """devuelve el path de url correspondiente al user"""
        return f'/user/{urlquote(self.username)}'

    @property
    def follower_count(self):
        """Devuelve la cantidad de seguidores que tiene este usuario"""
        return self.followers.count()
    
    def __str__(self):
        return self.username

class UserFCFM_Manager(BaseUserManager):
    """
    Definimos un UserManager customizado que nos permite crear y modificar a los usuarios.
    """
    use_in_migrations = True

    def _create_user(self, username, email, password, avatar, **extra_fields):
        """
        Crea y guarda un usuario con el username, email, contraseña y avatar dados.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.

        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, avatar=avatar **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()

class Post(models.Model):
    """
    Modelo que representa un Post
    """
    title = models.CharField(max_length=200)  # Título del post
    date = models.DateTimeField(auto_now_add=True)  # Fecha de creación del post (se genera automáticamente)
    content = models.TextField()  # Contenido del post
    user = models.ForeignKey(UserFCFM, on_delete=models.CASCADE)  # Relación con el modelo de Usuario
    game = models.ForeignKey(VideoGame, on_delete=models.CASCADE)  # Relación con el modelo Game

    @property
    def like_count(self):
        """Devuelve la cantidad de likes que tiene el post."""
        return self.liked_by.count()
    
    @property
    def url_title(self):
        """una version percent-encoded del titulo, para usarlo en urls"""
        return urlquote(self.title)

    def __str__(self):
        return self.title

class Follow(models.Model):
    """
    Representa la relación donde el usuario 'follower' sigue al usuario 'following'
    """
    follower = models.ForeignKey(UserFCFM, related_name = 'following', on_delete=models.CASCADE)
    following = models.ForeignKey(UserFCFM, related_name = 'followers', on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)