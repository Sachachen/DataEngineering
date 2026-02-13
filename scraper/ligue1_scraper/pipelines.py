from itemadapter import ItemAdapter
from pymongo import MongoClient
from datetime import datetime
import os
import logging


class MongoDBPipeline:
    """Pipeline pour stocker les données dans MongoDB"""
    
    collection_teams = 'ligue1_teams'
    collection_stats = 'ligue1_stats'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'ligue1_db')
        )

    def open_spider(self, spider):
        """Connexion à MongoDB au démarrage du spider"""
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info(f'Connected to MongoDB: {self.mongo_db}')

    def close_spider(self, spider):
        """Fermeture de la connexion MongoDB"""
        self.client.close()
        spider.logger.info('MongoDB connection closed')

    def process_item(self, item, spider):
        """Traitement et insertion des items"""
        adapter = ItemAdapter(item)
        
        # Ajouter la date de scraping si non présente
        if 'scraped_date' not in adapter.field_names() or not adapter.get('scraped_date'):
            adapter['scraped_date'] = datetime.now()
        
        # Détecter le type d'item et insérer dans la bonne collection
        item_type = type(item).__name__
        
        if 'Team' in item_type:
            # Mise à jour ou insertion d'une équipe
            self.db[self.collection_teams].update_one(
                {'equipe': adapter.get('equipe')},
                {'$set': dict(adapter)},
                upsert=True
            )
            spider.logger.info(f'Team saved: {adapter.get("equipe")}')
            
        elif 'Stats' in item_type:
            # Insertion des stats générales
            self.db[self.collection_stats].insert_one(dict(adapter))
            spider.logger.info(f'Stats saved for season: {adapter.get("saison")}')
        
        return item


class DataCleaningPipeline:
    """Pipeline pour nettoyer et valider les données"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Nettoyer les espaces dans les strings
        for field in adapter.field_names():
            value = adapter.get(field)
            if isinstance(value, str):
                adapter[field] = value.strip()
        
        # Convertir les champs numériques
        numeric_fields = ['position', 'points', 'matchs_joues', 'victoires', 
                         'nuls', 'defaites', 'buts_pour', 'buts_contre', 
                         'difference', 'total_equipes', 'total_matchs']
        
        for field in numeric_fields:
            if field in adapter.field_names():
                value = adapter.get(field)
                if value is not None:
                    try:
                        adapter[field] = int(value)
                    except (ValueError, TypeError):
                        spider.logger.warning(f'Could not convert {field} to int: {value}')
        
        return item
