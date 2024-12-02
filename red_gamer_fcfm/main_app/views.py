from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import VideoGame, UserFCFM, Post, Follow
from .forms import PostForm, UserFCFM_CreationForm, UserUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Count, Q
from django.contrib import messages
from django.core.exceptions import ValidationError
from urllib.parse import unquote
from http import HTTPStatus
from .utils import return_url

def index_all(request):
    if not request.user.is_authenticated:
        return redirect("/")

    return index(request, True)

def index(request, all=False):
    """Vista asociada al main landing page."""
    
    if request.method == 'POST':
        # POST: Cliente solicita y envia información (Boton de subir post).
        
        if not request.user.is_authenticated:
            # Redirige a la página principal sin hacer nada si no se esta autenticado.
            # Realmente ya no es necesario porque en ese caso el boton de subir esta oculto.
            return redirect('/')  
        
        # Si estabamos autenticados, leemos la informacion recibida del cliente.
        # y creamos un formulario de tipo PostForm (Definido en forms.py) a partir de la info.
        form = PostForm(request.POST)
        
        # Verificamos si dicha información es valida.
        if form.is_valid():
            post = form.save(commit=False)  # No guarda aún, porque necesitamos asignar el usuario.
            post.user = UserFCFM.objects.get(id=request.user.id)  # Asigna el usuario registrado.
            post.save()  # Ahora guarda el post con el usuario asignado.
            return redirect('/')  # Redirige a la página de posts.
    
    elif request.method == 'GET':
        # GET: Cliente solo solicita información.
        # Se define un form vacío.
        form = PostForm()
    
    posts_liked= []

    if request.user.is_authenticated:
        # Si iniciaste sesion, te muestra solo algunos posts:
        # - Los que son sobre un juego que sigues
        # - Los que publicó un usuario al que sigues
        # - Los que publicaste tú
        followed_users = set(f.following for f in Follow.objects.filter(follower=request.user))
        followed_games = request.user.followed_games.all()
        posts_liked= request.user.liked_posts.all()

        if all:
            posts = Post.objects.all().order_by('-date')
        
        else:
            posts = Post.objects.filter(Q(game__in=followed_games) | Q(user__in=followed_users) | Q(user=request.user)).order_by('-date')
    else:
        # Si no hay login hecho, recupera todos los posts a partir del modelo Post
        # y los ordena por fecha descendente.
        posts = Post.objects.all().order_by('-date')
    
    # Retornamos la información al cliente y renderizamos template, incluyendo las variables que se utilizarán.
    return render(request, "main_app/index.html", {'form': form, 'posts': posts, "posts_liked": posts_liked, "all": all })

def index_debug(request):
    """ Vista con links directos a todas las páginas, para debugging. """
    return render(request, "main_app/index_debug.html")

def register(request):
    """Vista simplificada asociada al formulario de registro de usuario."""

    if request.user.is_authenticated:
        # Si ya habías iniciado sesión, simplemente te devuelve al landing 
        # o a la página en la que estabas.
        return redirect(return_url(request))
    
    from_url = request.META['HTTP_REFERER']
    if request.method == 'POST':
        #Tras enviar el formulario de registro, validamos la información
        
        form = UserFCFM_CreationForm(request.POST)
        
        if form.is_valid():
            # Guardamos el formulario y creamos al usuario, iniciando tambien sesion.
            user = form.save()
            
            login(request, user)
            messages.success(request, f'Tu cuenta ha sido creada! Iniciando sesión.')

            # Retorna a la pagina anterior, si se especificó.
            return redirect(return_url(request))
        from_url = request.POST['goto']

    elif request.method == 'GET':
        form = UserFCFM_CreationForm()
    
    # Se renderiza la vista, pasando las variables a utilizar.
    return render(request, 'main_app/register.html', {'form': form, 'register': True, 'from_url': from_url})

def logout_user(request):
    """Vista asociada a la funcionalidad de cerrar sesión."""
    
    # Hacemos logout
    logout(request)
    
    # Se te redirige a la página en la que estabas.
    return HttpResponseRedirect(return_url(request))

def login_user(request):
    """Vista asociada a la funcionalida de iniciar sesión."""
    
    if request.user.is_authenticated:
        # Si ya habiamos hecho login, te devuelve a la pagina de la que viniste.
        return redirect(return_url(request))

    from_url = request.META['HTTP_REFERER']
    #Si se recibe un POST, se autentifica al usuario
    if request.method == 'POST':
        #Se recupera username y contraseña
        username = request.POST['username']
        password = request.POST['password']
        
        #Se autentifica al usuario (authenticate es de Django)
        user = authenticate(request, username=username, password=password)
        
        #Si el usuario existe, se loguea
        if user is not None:
            login(request, user)
            
            # manda a la pagina anterior, si se especificó
            return redirect(return_url(request))
        
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos')
            from_url = request.POST['goto']
    print()
    return render(request, 'main_app/login.html', {'login': True, 'from_url': from_url})

def user_page_posts(request, username):
    """Vista asociada a la página de perfil de un usuario, pestaña de posts."""
    
    #Obtenemos el usuario al que esta asociado username
    viewing = UserFCFM.objects.get(username=username)
    followed_users = []
    posts_liked= []
    if request.user.is_authenticated:
        follow_elements = request.user.following.all()
        followed_users = [follow.following for follow in follow_elements]
        posts_liked= request.user.liked_posts.all()

    
    # Recupera los posts del usuario y los ordena por fecha descendiente.
    posts = Post.objects.filter(user=viewing).order_by('-date')  
    
    return render(request, "main_app/user_page/posts.html", {'posts': posts, 'viewing': viewing, 'followed_users': followed_users,'posts_liked': posts_liked})

def user_page_games(request, username):
    """Vista asociada a la página de perfil de un usuario, pestaña de juegos."""
    
    #Obtenemos el usuario al que esta asociado username
    viewing = UserFCFM.objects.get(username=username)

    followed_users = []

    # Y los juegos que sigue el usuario que esta autenticado
    followed_games = []
    posts_liked= []

    # Recupera los juegos que sigue el usuario
    games = viewing.followed_games.all().order_by('name')

    if request.user.is_authenticated:
        follow_elements = request.user.following.all()
        followed_games = request.user.followed_games.all()
        followed_users = [follow.following for follow in follow_elements]
        posts_liked = request.user.liked_posts.all()

    
    return render(request, "main_app/user_page/games.html", {'games': games, 'viewing': viewing, 'followed_games': followed_games, 'followed_users': followed_users, 'posts_liked': posts_liked})

def user_page_followers(request, username):
    """ Vista asociada a la página de perfil de un usuario, pestaña de seguidores. """

    #Obtenemos el usuario al que esta asociado username
    viewing_user = UserFCFM.objects.get(username=username)

    followers = []
    followed_users = []

    #Obtenemos los elementos del modelo follow donde el usuario visualizado es "followed". (Es seguido)
    follow_elements_followed = viewing_user.followers.all().order_by('-created_at')

    #A partir de los elementos anteriores, extremos el campo/usuario seguidor.
    followers = [follow.follower for follow in follow_elements_followed]

    if request.user.is_authenticated:
        #Obtenemos los elementos del modelo follow donde el usuario logeado es el "follower" (Es el seguidor)
        follow_elements_follower = request.user.following.all()

        #A partir de los elementos anteriores, extraemos el campo/usuario seguido.
        followed_users = [follow.following for follow in follow_elements_follower]
    
    return render(request, "main_app/user_page/followers.html", {'followers': followers, 'viewing': viewing_user, 'followed_users': followed_users})

def settings(request):
    """ Vista correspondiente a la página de edición de datos del usuario """

    # si no estas autenticado/a, te devuielve a donde estabas
    if not request.user.is_authenticated:
        return redirect(return_url(request))

    if request.method == 'POST':
        # si es post, actualiza los datos
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_posts', username=request.user.username)
    else:
        # si no, solo devuelve el formulario
        form = UserUpdateForm(instance=request.user)
    return render(request, 'main_app/user_page/settings.html', {'form': form})

def game_index(request):
    """Vista asociada a la página de índice de videojuegos"""
    
    query = request.GET.get('q', '') # parámetro de filtro

    # Si el formulario se envía, procesar el género seleccionado
    # Todos es la opcion por defecto.
    selected_genre = request.POST.get('select-genre', 'Todos')
    
    # Recupera todos los juegos, ordenados por cantidad de followers
    # hacerlo con anotacion es mas rapido, pues lo calcula el engine de sql
    # y no python. Ademas, evita mas llamadas a sql para mostrarlos en la interfaz
    if selected_genre == 'Todos':
        games = VideoGame.objects.all() \
            .annotate(followers=Count('followed_by')) \
            .order_by('-followers', 'name')
    else:
        games = VideoGame.objects.filter(genre = selected_genre) \
            .annotate(followers=Count('followed_by')) \
            .order_by('-followers', 'name')
    
    followed_games = []
    
    #Obtenemos los juegos que el usuario sigue, si es que esta autenticado.
    if request.user.is_authenticated:
        followed_games = request.user.followed_games.all()

    #obtenemos una lista con todos los géneros posibles de videojuego en la base de datos.
    genres = VideoGame.objects.values('genre').distinct()
    
    return render(request, 'main_app/indexes/game_index.html', {'games': games, 'query': unquote(query), 'followed_games': followed_games, 'genres': genres, 'selected_genre': selected_genre})

def follow_game(request, game_name):
    """
    Vista/Código asociado a la funcionalidad de seguir juegos.
    Permite seguir/dejar de seguir un juego mediante una solicitud
    autenticada a /follow_game/<juego>
    """
    
    if request.user.is_authenticated:
        # si esta autenticado, obtengo el juego
        game = VideoGame.objects.get(name=unquote(game_name))
        
        # si ya lo sigue, lo des-sigue,
        # si no lo sigue, lo sigue
        if request.user.followed_games.filter(pk=game.pk).exists():
            request.user.followed_games.remove(game)
        else:
            request.user.followed_games.add(game)

    ret_url = return_url(request, {'s': 'true'})

    return redirect(ret_url)

def follow_user(request, username):
    """
    Permite seguir/dejar de seguir a un usuario mediante una solicitud
    autenticada a /follow_user/<juego>
    """
    if request.user.is_authenticated:
        #Si estamos autenticados, obtenemos el user que queremos seguir
        user_to_follow = get_object_or_404(UserFCFM, username = unquote(username))

        #Obtenemos la lista de usuarios que seguimos, y verificamos si este usuario existe ahi.
        #Esta lista hace referencia al modelo Follow, y contiene following, follower y date.
        
        if not request.user.following.filter(follower = request.user, following = user_to_follow).exists():
            #Si el usuario no existe, creamos la relacion de seguimiento en Follow
            Follow.objects.create(follower = request.user, following = user_to_follow)
        else:
            #Si el usuario ya existia, eliminamos la relacion de follow
            request.user.following.filter(follower = request.user, following = user_to_follow).delete()
    
    ret_url = return_url(request, {'s': 'true'})

    return redirect(ret_url)


def user_index(request):
    """ Vista asociada a la página de índice de usuarios """
    
    #Parámetro para filtrar
    query = request.GET.get('q', '')

    # Si el formulario se envía, procesar el género seleccionado
    # Todos es la opcion por defecto.
    selected_genre = request.POST.get('select-genre', 'Todos')

    # En la variable users recuperamos todos los usuarios para mostrarlos (Menos el usuario autenticado), 
    # ordenados por cantidad de followers. hacerlo con anotacion es mas rapido, pues lo calcula el engine de sql
    # y no python. Ademas, evita mas llamadas a sql para mostrarlos en la interfaz.

    #En la variable followed_users guardamos todos los usuarios que el usuario autenticado sigue.

    followed_users = []

    non_admin_users = UserFCFM.objects.filter(is_superuser = False)

    if request.user.is_authenticated:
        if selected_genre == 'Todos':
            #Mostramos los usuarios que siguen juegos de todos los generos, menos al usuario autenticado
            users = non_admin_users.exclude(username = request.user.username) \
            .annotate(total_followers=Count('followers')) \
            .order_by('-total_followers', 'username')
        else:
            #Mostramos los usuarios que siguen juegos del genero seleccionado, menos al usuario autenticado.
            #el doble underscore (__) permite filtrar por aquellos usuarios donde alguno de los elementos en la relacion followed_games tenga el atributo genre buscado.
            users = UserFCFM.objects.filter(is_superuser = False, followed_games__genre=selected_genre).exclude(username = request.user.username).distinct() \
            .annotate(total_followers=Count('followers')) \
            .order_by('-total_followers', 'username')

        #Obtenemos los elementos de follow donde el usuario es el follower
        follow_elements = request.user.following.all()

        #De los elementos de follow extraemos el usuario que es seguido (followed)
        followed_users = [follow.following for follow in follow_elements]
    else:
        if selected_genre == 'Todos':
            #Si no estamos autenticados, no excluimos al usuario de la query, y no rellenamos followed_users. No filtramos por genero seleccionado.
            users = non_admin_users \
            .annotate(total_followers=Count('followers')) \
            .order_by('-total_followers', 'username')
        else:
            #Filtramos por usuarios que siguen algun juego del genero seleccionado
            users = UserFCFM.objects.filter(is_superuser = False, followed_games__genre=selected_genre).distinct() \
            .annotate(total_followers=Count('followers')) \
            .order_by('-total_followers', 'username')

        
    #obtenemos una lista con todos los géneros posibles de videojuego en la base de datos.
    genres = VideoGame.objects.values('genre').distinct()

    return render(request, 'main_app/indexes/user_index.html', {'users': users, 'query': unquote(query), 'followed_users': followed_users, 'genres': genres, 'selected_genre': selected_genre})

def game_page(request,game_name):
    """ Vista correspondiente a la página de cada juego"""
    #Obtenemos el videojuego que se solicita para la pagina
    game_requested = VideoGame.objects.get(name = game_name)

    #Obtenemos los seguidores del juego deseado
    followers = game_requested.follow_count

    followed_games = []
    posts_liked= []
    
    #Obtenemos los juegos que el usuario sigue, y los posts a los que le ha hecho like si es que esta autenticado.
    if request.user.is_authenticated:
        followed_games = request.user.followed_games.all()
        posts_liked= request.user.liked_posts.all()
    
    # Recupera los posts del videojuego y los ordena por fecha descendiente.
    posts = Post.objects.filter(game=game_requested).order_by('-date')

    
    return render(request, "main_app/game_page/posts.html", {'posts': posts, 'game_requested': game_requested, "followers": followers, "followed_games":followed_games, "posts_liked": posts_liked})

def like_post(request, post_id):
    """
    Vista/Código asociado a la funcionalidad de dar like a un post.
    Permite dar/quitar like a un Post mediante una solicitud
    autenticada a /like_post/<post>
    """
    print(post_id)
    
    if request.user.is_authenticated:
        # si esta autenticado, obtengo el post
        post = Post.objects.get(id=unquote(post_id))
        
        # si ya le dio like, lo des-likea,
        # si no , da like
        if request.user.liked_posts.filter(pk=post.pk).exists():
            request.user.liked_posts.remove(post)
        else:
            request.user.liked_posts.add(post)

    ret_url = return_url(request, {'s': 'true'})

    return redirect(ret_url)
