
# Red Gamer

Una red social simple que permite a los usuarios publicar sobre sus juegos favoritos.

## _Features_
- Creación de cuentas e Inicio de Sesión
- Publicaciones asociadas a uno de los juego disponibles en la Base de Datos
- Seguir Juegos y Personas
- Ver las últimas publicaciones
- Ver las últimas publicaciones de juegos o personas que sigues
- Ver el perfil de un usuario, con sus publicaciones, juegos seguidos y seguidores
- Ver las publicaciones asociadas a un juego
- Ver una lista de todos los usuarios, y buscar por nombre y por género de juegos que sigue
- Ver una lista de todos los juegos, y buscar por nombre y por género
- Dar _like_ a las publicaciones

### Para correr

```bash
git clone https://github.com/epzita/django_social_network
python -m venv /.venv
source ./venv/bin/activate
cd red-gamer-fcfm
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
Y luego ingresar a `localhost:8000` en tu navegador
