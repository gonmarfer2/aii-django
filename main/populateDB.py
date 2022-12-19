#encoding:utf-8
from main.models import  Anime, Puntuacion


path = "data"

def populate():
    a=populateAnime()
    p=populatePuntuacion()  #USAMOS LOS DICCIONARIOS DE USUARIOS Y PELICULAS PARA ACELERAR LA CARGA EN PUNTUACIONES
    return (a,p)

def populateAnime():
    Anime.objects.all().delete()
    lista=[]
    fileobj=open(path+"\\anime.txt", "r")
    fileobj.readline()
    for line in fileobj.readlines():
        rip = str(line.strip()).split('\t')
        


        if rip[4].strip()!='Unknown':
            numEpisodios=int(rip[4].strip())
        else:
            numEpisodios=None
        lista.append(Anime(animeId=int(rip[0].strip()), titulo=str(rip[1].strip()),genero=str(rip[2].strip()), formatoEmision=str(rip[3].strip()), numEpisodios=numEpisodios))
    fileobj.close()
    Anime.objects.bulk_create(lista)   
    return Anime.objects.count()

def populatePuntuacion():
    Puntuacion.objects.all().delete()
    
    lista=[]
    fileobj=open(path+"\\ratings.txt", "r")
    fileobj.readline()
    for line in fileobj.readlines():
        rip = str(line.strip()).split('\t')
        lista.append(Puntuacion(idUsuario=int(rip[0].strip()),animeId=Anime.objects.get(animeId=int(rip[1].strip())),puntuacion=str(rip[2].strip())))
    fileobj.close()
    Puntuacion.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return len(lista)