"""
Package contenant les spiders Scrapy pour la collecte de données Ligue 1

Spiders disponibles:
    - ligue1: Scrape le classement de la Ligue 1 depuis Wikipedia
    
Utilisation:
    scrapy crawl ligue1
"""

from .ligue1_spider import Ligue1Spider

__all__ = [
    'Ligue1Spider',
]

__version__ = '1.0.0'
__author__ = 'Ligue 1 Analytics Team'
