#!/usr/bin/env python3
"""
Scheduler pour lancer le spider Ligue 1 périodiquement
"""
import schedule
import time
import subprocess
import logging
import sys
import argparse
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_spider():
    """Lance le spider Ligue 1"""
    logger.info('🕷️  Starting Ligue 1 spider...')
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'ligue1'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        if result.returncode == 0:
            logger.info('✅ Spider completed successfully')
        else:
            logger.error(f'❌ Spider failed with code {result.returncode}')
            logger.error(f'Error: {result.stderr}')
            
    except subprocess.TimeoutExpired:
        logger.error('❌ Spider timeout after 5 minutes')
    except Exception as e:
        logger.error(f'❌ Error running spider: {e}')


def main():
    """Fonction principale du scheduler"""
    parser = argparse.ArgumentParser(description='Ligue 1 Spider Scheduler')
    parser.add_argument(
        '--immediate',
        action='store_true',
        help='Run spider immediately on startup'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=6,
        help='Interval in hours between scraping (default: 6)'
    )
    
    args = parser.parse_args()
    
    logger.info('🚀 Ligue 1 Scheduler started')
    logger.info(f'📅 Scraping interval: every {args.interval} hours')
    
    # Lancer immédiatement si demandé
    if args.immediate:
        logger.info('🔥 Running spider immediately on startup')
        run_spider()
    
    # Planifier les exécutions périodiques
    schedule.every(args.interval).hours.do(run_spider)
    
    logger.info('⏰ Scheduler is running. Press Ctrl+C to stop.')
    
    # Boucle principale
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    except KeyboardInterrupt:
        logger.info('👋 Scheduler stopped by user')
    except Exception as e:
        logger.error(f'❌ Scheduler error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
