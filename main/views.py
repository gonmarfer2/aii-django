#encoding:utf-8
from main.models import Usuario, Puntuacion, Pelicula
from main.populateDB import populate
from main.forms import  UsuarioBusquedaForm, PeliculaBusquedaYearForm
from django.shortcuts import render,redirect
from django.db.models import Avg, Count
from django.http.response import HttpResponseRedirect
from django.conf import settings
import shelve
from .forms import CustomAuthenticationForm

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .recommendations import *

#Funcion de acceso restringido que carga los datos en la BD  
@login_required(login_url='/ingresar')
def populateDatabase(request):
    (o,g,u,m,p)=populate()
    mensaje = 'Se han cargado: ' + str(o) + ' ocupaciones ;' + str(g) + ' generos ;' + str(u) + ' usuarios ;' + str(m) + ' peliculas ;' + str(p) + ' puntuaciones'
    logout(request)  # se hace logout para obligar a login cada vez que se vaya a poblar la BD
    return render(request, 'mensaje.html',{'titulo':'FIN DE CARGA','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})

def mostrar_ocupaciones(request):
    usuarios= Usuario.objects.all().order_by('ocupacion')
    return render(request, 'ocupacion_usuarios.html',{'usuarios':usuarios, 'STATIC_URL':settings.STATIC_URL})

# el parámetro pag es para indicar la página que queremos mostrar (paginador uikit). Cada página es de 10 películas
def mostrar_mejores_peliculas(request,pag):
    if pag > 5:
        pag = 5
    else:
        if pag < 1:
            pag = 1
    #peliculas con más de 100 puntuaciones
    peliculas = Pelicula.objects.annotate(avg_rating=Avg('puntuacion__puntuacion'),num_rating=Count('puntuacion__puntuacion')).filter(num_rating__gt=100).order_by('-avg_rating')[(pag-1)*10:pag*10]
    return render(request, 'mejores_peliculas.html', {'peliculas':peliculas, 'pagina':pag, 'STATIC_URL':settings.STATIC_URL})

def mostrar_peliculas_year(request):
    formulario = PeliculaBusquedaYearForm()
    peliculas = None
    anyo = None
    
    if request.method=='POST':
        formulario = PeliculaBusquedaYearForm(request.POST)
        
        if formulario.is_valid():
            anyo=formulario.cleaned_data['year']
            peliculas = Pelicula.objects.filter(fechaEstreno__year=anyo)
    
    return render(request, 'busqueda_peliculas.html', {'formulario':formulario, 'peliculas':peliculas, 'anyo':anyo, 'STATIC_URL':settings.STATIC_URL})

def mostrar_puntuaciones_usuario(request):
    formulario = UsuarioBusquedaForm()
    puntuaciones = None
    idusuario = None
    errores = set()
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idusuario = formulario.cleaned_data['idUsuario']
            try:
                puntuaciones = Puntuacion.objects.filter(idUsuario = Usuario.objects.get(pk=idusuario))
            except Usuario.DoesNotExist:
                errores.add("No existe el usuario")
            
    return render(request, 'puntuaciones_usuario.html', {'formulario':formulario, 'puntuaciones':puntuaciones, 'idusuario':idusuario, 'errores':errores, 'STATIC_URL':settings.STATIC_URL})

def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})

def ingresar(request):
    if request.user.is_authenticated:
        return(HttpResponseRedirect('/populate'))
    formulario = CustomAuthenticationForm()
    if request.method=='POST':
        formulario = CustomAuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/populate'))
            else:
                return render(request, 'mensaje.html',{'titulo':'ERROR','mensaje':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje.html',{'titulo':'ERROR','mensaje':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})

@login_required(login_url='/ingresar')
def cargarSR(request):
    with shelve.open('matriz') as db:
        prefs = {}
        for punt in Puntuacion.objects.all():
            itemId = punt.idPelicula.idPelicula
            userId = punt.idUsuario
            puntuacion = punt.puntuacion
            prefs.setdefault(userId,{})
            prefs[userId][itemId] = puntuacion
        db['prefs'] = prefs
        db['itemPrefs'] = transformPrefs(prefs)

        db['similarItems'] = calculateSimilarItems(prefs)
    
    return redirect('/')

def recomendar2peliculas(request):
    HTML_NAME = 'recomendar.html'
    if request.method == "GET":
        return render(request,HTML_NAME,{'form':UsuarioBusquedaForm(),'STATIC_URL':settings.STATIC_URL})
    elif request.method == "POST":
        usuario_form = UsuarioBusquedaForm(request.POST)
        if usuario_form.is_valid():
            try:
                usuario = Usuario.objects.get(pk=int(usuario_form.data.get('idUsuario')))
                
                with shelve.open('matriz.dat') as db:
                    dos_peliculas = getRecommendations(db['prefs'],usuario)[:2]
                    peliculas = [(Pelicula.objects.get(pk=p[1]),p[0]) for p in dos_peliculas]
                    #dos_peliculas = list(map(lambda pid : Pelicula.objects.get(pk=pid), dos_peliculas))
                    return render(request,HTML_NAME,{
                        'form':UsuarioBusquedaForm(request.POST),
                        'usuario':usuario.pk,
                        'peliculas':peliculas,
                        'STATIC_URL':settings.STATIC_URL
                    })
            except Usuario.DoesNotExist:
                return render(request,HTML_NAME,{
                    'form':UsuarioBusquedaForm(request.POST),
                    'errors':{'No existe el usuario ingresado'},
                    'STATIC_URL':settings.STATIC_URL
                })

        else:
           return render(request,HTML_NAME,{
            'form':UsuarioBusquedaForm(request.POST),
            'STATIC_URL':settings.STATIC_URL,
            }) 

def recomendar2peliculasD(request):
    HTML_NAME = 'recomendar2.html'
    if request.method == "GET":
        return render(request,HTML_NAME,{'form':UsuarioBusquedaForm(),'STATIC_URL':settings.STATIC_URL})
    elif request.method == "POST":
        usuario_form = UsuarioBusquedaForm(request.POST)
        if usuario_form.is_valid():
            try:
                
                usuario = Usuario.objects.get(pk=int(usuario_form.data.get('idUsuario')))
                with shelve.open('matriz.dat') as db:
                    tres_peliculas = getRecommendedItems(db['prefs'],db['similarItems'],usuario)[:3]
                    peliculas = [(Pelicula.objects.get(pk=p[1]),p[0]) for p in tres_peliculas]
                    #dos_peliculas = list(map(lambda pid : Pelicula.objects.get(pk=pid), dos_peliculas))
                    return render(request,HTML_NAME,{
                        'form':UsuarioBusquedaForm(request.POST),
                        'usuario':usuario.pk,
                        'peliculas':peliculas,
                        'STATIC_URL':settings.STATIC_URL
                    })
            except Usuario.DoesNotExist:
                return render(request,HTML_NAME,{
                    'form':UsuarioBusquedaForm(request.POST),
                    'errors':{'No existe el usuario ingresado'},
                    'STATIC_URL':settings.STATIC_URL
                })

        else:
           return render(request,HTML_NAME,{
            'form':UsuarioBusquedaForm(request.POST),
            'STATIC_URL':settings.STATIC_URL,
            }) 

        
