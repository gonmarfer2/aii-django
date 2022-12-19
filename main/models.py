#encoding:utf-8
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Anime(models.Model):
    animeId=models.IntegerField(primary_key=True)
    titulo=models.CharField(max_length=30, verbose_name='Título')
    genero=models.TextField(verbose_name='genero')
    formatoEmision=models.CharField(max_length=50, verbose_name='formato Emisión')
    numEpisodios=models.PositiveIntegerField(verbose_name='Número de Episodios', null=True)

class Puntuacion(models.Model):
    idUsuario = models.PositiveIntegerField(verbose_name='Id del usuario')
    animeId= models.ForeignKey(Anime, on_delete=models.SET_NULL, null=True)
    PUNTUACIONES = ((1, '1'), (2,'2'), (3,'3'), (4,'4'), (5,'5'),(6,'6'),(7,'7'),(8,'8'),(9,'9'),(10,'10'))
    puntuacion = models.PositiveSmallIntegerField(verbose_name='Puntuación', validators=[MinValueValidator(0), MaxValueValidator(10)], choices=PUNTUACIONES)
    def __str__(self):
        return (str(self.puntuacion))
    
    class Meta:
        ordering=('idUsuario','animeId', )