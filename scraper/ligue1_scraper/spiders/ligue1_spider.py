import scrapy
from ligue1_scraper.items import Ligue1TeamItem, Ligue1StatsItem
from datetime import datetime
import re


class Ligue1Spider(scrapy.Spider):
    """Spider pour scraper le classement de la Ligue 1 depuis Wikipedia"""
    
    name = "ligue1"
    allowed_domains = ["fr.wikipedia.org"]
    start_urls = ["https://fr.wikipedia.org/wiki/Championnat_de_France_de_football_2025-2026"]
    
    def parse(self, response):
        self.logger.info(f'Scraping: {response.url}')
        
        # Trouver le tableau de classement
        table = self._find_ranking_table(response)
        if not table:
            self.logger.error('Tableau de classement introuvable')
            return
        
        # Parser les données
        teams_count = 0
        journee = 0
        
        for row in table.css('tr')[1:]:  # Skip header
            team_data = self._parse_team_row(row)
            if not team_data:
                continue
            
            if journee == 0:
                journee = team_data['matchs_joues']
            
            yield Ligue1TeamItem(**team_data)
            teams_count += 1
            self.logger.info(f"{team_data['position']}. {team_data['equipe']} - {team_data['points']} pts")
        
        # Stats globales
        yield Ligue1StatsItem(
            saison="2025-2026",
            journee=journee,
            total_equipes=teams_count,
            total_matchs=0,
            scraped_date=datetime.now()
        )
        
        self.logger.info(f'✅ {teams_count} équipes scrapées')
    
    def _find_ranking_table(self, response):
        """Trouve le tableau de classement dans la page"""
        # Essayer différents sélecteurs
        for selector in ['table.wikitable', 'table']:
            tables = response.css(selector)
            if not tables:
                continue
            
            # Chercher le bon tableau
            for table in tables:
                text = ' '.join(table.css('::text').getall())
                # Le tableau doit contenir "Pts" et au moins une équipe connue
                if 'Pts' in text and any(team in text for team in ['Paris Saint-Germain', 'Lens', 'Monaco']):
                    return table
        
        return None
    
    def _parse_team_row(self, row):
        """Parse une ligne du tableau pour extraire les données d'une équipe"""
        cells = row.css('td')
        
        if len(cells) < 8:
            return None
        
        try:
            # Position
            pos_text = cells[0].css('::text').get()
            if not pos_text:
                return None
            position = int(re.search(r'\d+', pos_text).group())
            
            # Nom de l'équipe
            equipe = (cells[1].css('a::text').get() or 
                     cells[1].css('::text').get() or
                     cells[2].css('a::text').get() or 
                     cells[2].css('::text').get() or "Unknown").strip()
            
            # Extraction des nombres (Pts, J, V, N, D, BP, BC, Diff)
            numbers = []
            for cell in cells[2:]:
                text = cell.css('::text').get(default='').strip()
                match = re.search(r'-?\d+', text)
                if match:
                    numbers.append(int(match.group()))
            
            if len(numbers) < 8:
                return None
            
            return {
                'position': position,
                'equipe': equipe,
                'points': numbers[0],
                'matchs_joues': numbers[1],
                'victoires': numbers[2],
                'nuls': numbers[3],
                'defaites': numbers[4],
                'buts_pour': numbers[5],
                'buts_contre': numbers[6],
                'difference': numbers[7],
                'forme': "",
                'scraped_date': datetime.now()
            }
            
        except Exception as e:
            self.logger.debug(f'Erreur parsing ligne: {e}')
            return None
