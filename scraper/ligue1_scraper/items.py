import scrapy
from datetime import datetime


class Ligue1TeamItem(scrapy.Item):
    """Item pour les équipes de Ligue 1"""
    position = scrapy.Field()           # Classement (1-20)
    equipe = scrapy.Field()             # Nom de l'équipe
    points = scrapy.Field()             # Points totaux
    matchs_joues = scrapy.Field()       # Nombre de matchs joués
    victoires = scrapy.Field()          # Nombre de victoires
    nuls = scrapy.Field()               # Nombre de nuls
    defaites = scrapy.Field()           # Nombre de défaites
    buts_pour = scrapy.Field()          # Buts marqués
    buts_contre = scrapy.Field()        # Buts encaissés
    difference = scrapy.Field()         # Différence de buts
    forme = scrapy.Field()              # Forme récente (5 derniers matchs)
    scraped_date = scrapy.Field()       # Date du scraping


class Ligue1StatsItem(scrapy.Item):
    """Item pour les statistiques générales"""
    saison = scrapy.Field()             # Saison (ex: "2025-2026")
    journee = scrapy.Field()            # Journée en cours
    total_equipes = scrapy.Field()      # Nombre total d'équipes
    total_matchs = scrapy.Field()       # Total de matchs joués
    scraped_date = scrapy.Field()       # Date du scraping
