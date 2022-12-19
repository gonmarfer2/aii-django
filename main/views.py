#encoding:utf-8
from main.models import Anime, Puntuacion
from main.populateDB import populate
from main.forms import  UsuarioBusquedaForm, PeliculaBusquedaYearForm, GeneroForm
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
def populateDatabase(request):
    if request.method=='GET':
        return render(request,'confirmation.html',{'STATIC_URL':settings.STATIC_URL})
    else:
        (a,p)=populate()
        mensaje = 'Se han cargado: ' +' Tipos de emisiones ;' + str(a) + ' animes (UwU) ;' + str(p) + ' puntuaciones ;'
        return render(request, 'mensaje.html',{'titulo':'FIN DE CARGA','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})

def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})

def cargarSR(request):
    with shelve.open('matriz') as db:
        prefs = {}
        for punt in Puntuacion.objects.all():
            itemId = int(punt.animeId.animeId)
            userId = int(punt.idUsuario)
            puntuacion = int(punt.puntuacion)
            prefs.setdefault(userId,{})
            prefs[userId][itemId] = puntuacion
        db['prefs'] = prefs
        db['itemPrefs'] = transformPrefs(prefs)

        db['similarItems'] = calculateSimilarItems(prefs)
        print(db['prefs'][3])
    
    return render(request,'mensaje.html',{'mensaje':'Se han cargado las matrices satisfactoriamente','STATIC_URL':settings.STATIC_URL})

def peliculaPorGenero(request):

    generos_dict = get_generos()
    generos = [g for g in generos_dict]
    if request.method == 'POST':
            form = GeneroForm(request.POST)
            if form.is_valid():
                animes = generos_dict.get(request.POST['genero'])
                animes = sorted(animes, key= lambda x: x.formatoEmision)
                return render(request,'genero.html',{'form':form,'animes':animes, 'generos':generos, 'STATIC_URL':settings.STATIC_URL})
            else:
                # TRADUCCION
                return render(request,'genero.html',{'errors':['Found error in the form']})
    else:
        form = GeneroForm()
    return render(request,'genero.html',{'form':form, 'generos': generos, 'STATIC_URL':settings.STATIC_URL})

def get_generos():
    res = {}
    animes = Anime.objects.all()
    for anime in animes:
        for genero in anime.genero.split(","):
            if genero.strip() in res:
                res.get(genero.strip()).append(anime)
            else:
                res[genero.strip()] = []
                res.get(genero.strip()).append(anime)
    return res

def recomendar_animes(request):
    HTML_NAME = 'recomendar.html'
    if request.method == "GET":
        return render(request,HTML_NAME,{'form':UsuarioBusquedaForm(),'STATIC_URL':settings.STATIC_URL})
    elif request.method == "POST":
        usuario_form = UsuarioBusquedaForm(request.POST)
        if usuario_form.is_valid():
            try:
                usuario = int(usuario_form.data.get('idUsuario'))
                with shelve.open('matriz') as db:
                    tres_animes = getRecommendedItems(db['prefs'],db['similarItems'],usuario)[:3]
                    animes = [(Anime.objects.get(pk=a[1]),a[0]) for a in tres_animes]
                    return render(request,HTML_NAME,{
                        'form':UsuarioBusquedaForm(request.POST),
                        'usuario':usuario,
                        'animes':animes,
                        'STATIC_URL':settings.STATIC_URL
                    })
            except:
                return render(request,HTML_NAME,{
                        'form':UsuarioBusquedaForm(request.POST),
                        'usuario':usuario,
                        'errors':{'No existe el usuario'},
                        'STATIC_URL':settings.STATIC_URL
                    })

        else:
           return render(request,HTML_NAME,{
            'form':UsuarioBusquedaForm(request.POST),
            'STATIC_URL':settings.STATIC_URL,
            })

def mejores_animes(request):
    mejores_animes = Puntuacion.objects.values('animeId').annotate(avg_puntuacion=Avg('puntuacion')).order_by('-avg_puntuacion')[:3]
    mejores_animes = [(Anime.objects.get(animeId=a.get('animeId')),a.get('avg_puntuacion')) for a in mejores_animes]
    return render(request,'mejoresanimes.html',{'mejores_animes':mejores_animes,'STATIC_URL':settings.STATIC_URL})
