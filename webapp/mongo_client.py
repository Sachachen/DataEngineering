from pymongo import MongoClient
import os
import logging

logger = logging.getLogger(__name__)


class MongoDBClient:
    """Client MongoDB pour récupérer les données"""
    
    def __init__(self):
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@mongodb:27017/ligue1_db?authSource=admin')
        self.db_name = os.getenv('MONGO_DB', 'ligue1_db')
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connexion à MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            # Test de connexion
            self.client.admin.command('ping')
            logger.info(f'Connected to MongoDB: {self.db_name}')
        except Exception as e:
            logger.error(f'MongoDB connection error: {e}')
            raise
    
    def get_teams(self, limit=20):
        """Récupère les équipes triées par classement"""
        try:
            teams = list(self.db.ligue1_teams.find(
                {},
                {'_id': 0}
            ).sort('position', 1).limit(limit))
            return teams
        except Exception as e:
            logger.error(f'Error fetching teams: {e}')
            return []
    
    def get_top_scorers(self, limit=10):
        """Récupère les équipes avec le plus de buts marqués"""
        try:
            scorers = list(self.db.ligue1_teams.find(
                {},
                {'_id': 0, 'equipe': 1, 'buts_pour': 1, 'position': 1}
            ).sort('buts_pour', -1).limit(limit))
            return scorers
        except Exception as e:
            logger.error(f'Error fetching top scorers: {e}')
            return []
    
    def get_stats(self):
        """Récupère les statistiques générales"""
        try:
            # Statistiques depuis la dernière entrée
            stats = self.db.ligue1_stats.find_one({}, {'_id': 0}, sort=[('scraped_date', -1)])
            
            if not stats:
                # Calculer depuis les équipes si pas de stats
                teams_count = self.db.ligue1_teams.count_documents({})
                stats = {
                    'total_equipes': teams_count,
                    'saison': '2025-2026'
                }
            
            return stats
        except Exception as e:
            logger.error(f'Error fetching stats: {e}')
            return {}
    
    def get_total_teams(self):
        """Compte le nombre total d'équipes"""
        try:
            return self.db.ligue1_teams.count_documents({})
        except Exception as e:
            logger.error(f'Error counting teams: {e}')
            return 0
    
    def get_total_goals(self):
        """Calcule le total de buts marqués"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_buts': {'$sum': '$buts_pour'}
                    }
                }
            ]
            result = list(self.db.ligue1_teams.aggregate(pipeline))
            return result[0]['total_buts'] if result else 0
        except Exception as e:
            logger.error(f'Error calculating total goals: {e}')
            return 0
    
    def close(self):
        """Ferme la connexion"""
        if self.client:
            self.client.close()
            logger.info('MongoDB connection closed')
