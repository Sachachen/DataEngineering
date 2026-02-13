#!/usr/bin/env python3
"""
Health Check Script
Vérifie que tous les services de la plateforme Ligue 1 Analytics fonctionnent correctement
"""
import requests
import sys
from pymongo import MongoClient
from datetime import datetime
import os

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")

def check_mongodb():
    """Check MongoDB connection and data"""
    print_header("MONGODB CHECK")
    
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@localhost:27017/ligue1_db?authSource=admin')
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print_success("MongoDB connection successful")
        
        db = client.ligue1_db
        
        # Check collections
        collections = {
            'players': db.players.count_documents({}),
            'surface_stats': db.surface_stats.count_documents({}),
            'matches': db.matches.count_documents({}),
            'tournaments': db.tournaments.count_documents({})
        }
        
        total_docs = sum(collections.values())
        
        if total_docs == 0:
            print_warning("Database is empty - run init_data.py or scraping")
        else:
            print_success(f"Database has {total_docs} total documents")
            for collection, count in collections.items():
                status = "✓" if count > 0 else "✗"
                print(f"  {status} {collection}: {count} documents")
        
        client.close()
        return True
        
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        return False

def check_api():
    """Check API service"""
    print_header("API CHECK")
    
    api_url = "http://localhost:8000"
    
    try:
        # Test root endpoint
        response = requests.get(f"{api_url}/", timeout=5)
        if response.status_code == 200:
            print_success("API root endpoint accessible")
        else:
            print_error(f"API returned status {response.status_code}")
            return False
        
        # Test summary endpoint
        response = requests.get(f"{api_url}/api/stats/summary", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("API stats endpoint working")
            print(f"  Total players: {data.get('total_players', 0)}")
            print(f"  Total matches: {data.get('total_matches', 0)}")
            print(f"  Total tournaments: {data.get('total_tournaments', 0)}")
        else:
            print_warning(f"Stats endpoint returned status {response.status_code}")
        
        # Test players endpoint
        response = requests.get(f"{api_url}/api/players?limit=5", timeout=5)
        if response.status_code == 200:
            players = response.json()
            print_success(f"Players endpoint working (returned {len(players)} players)")
        else:
            print_warning(f"Players endpoint returned status {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API - is it running?")
        print_info("Start with: docker-compose up api")
        return False
    except Exception as e:
        print_error(f"API check failed: {e}")
        return False

def check_dashboard():
    """Check Dashboard service"""
    print_header("DASHBOARD CHECK")
    
    dashboard_url = "http://localhost:8050"
    
    try:
        response = requests.get(dashboard_url, timeout=5)
        if response.status_code == 200:
            print_success("Dashboard is accessible")
            print_info(f"Visit: {dashboard_url}")
        else:
            print_error(f"Dashboard returned status {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Dashboard - is it running?")
        print_info("Start with: docker-compose up webapp")
        return False
    except Exception as e:
        print_error(f"Dashboard check failed: {e}")
        return False

def check_docker():
    """Check Docker containers"""
    print_header("DOCKER CHECK")
    
    try:
        import subprocess
        
        result = subprocess.run(
            ['docker-compose', 'ps', '--format', 'json'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print_success("Docker Compose is available")
            
            # Check if containers are running
            ps_result = subprocess.run(
                ['docker-compose', 'ps'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if "Up" in ps_result.stdout:
                print_success("Some containers are running")
                print(ps_result.stdout)
            else:
                print_warning("No containers appear to be running")
                print_info("Start with: docker-compose up -d")
        else:
            print_warning("Docker Compose command failed")
            
        return True
        
    except FileNotFoundError:
        print_warning("Docker Compose not found in PATH")
        return False
    except Exception as e:
        print_warning(f"Docker check failed: {e}")
        return False

def main():
    """Run all health checks"""
    print(f"\n{Colors.BOLD}⚽ Ligue 1 Analytics Platform - Health Check{Colors.END}")
    print(f"{Colors.BOLD}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    checks = {
        'Docker': check_docker(),
        'MongoDB': check_mongodb(),
        'API': check_api(),
        'Dashboard': check_dashboard()
    }
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for service, status in checks.items():
        if status:
            print_success(f"{service}: OK")
        else:
            print_error(f"{service}: FAILED")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All systems operational!{Colors.END}\n")
        print("You can access:")
        print(f"  • Dashboard: http://localhost:8050")
        print(f"  • API: http://localhost:8000")
        print(f"  • API Docs: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some checks failed{Colors.END}\n")
        print("Troubleshooting:")
        print("  1. Ensure Docker containers are running: docker-compose up -d")
        print("  2. Check logs: docker-compose logs")
        print("  3. Initialize data: python init_data.py")
        print("  4. See QUICKSTART.md for detailed instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())
