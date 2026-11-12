
# Risky database configuration - DEMO ONLY

DATABASE_HOST = "localhost"
DATABASE_PORT = 5432

# Hardcoded credentials (intentionally insecure)
DATABASE_USER = "admin"
DATABASE_PASSWORD = "admin123"

# Risky configuration
DEBUG = True
SSL_ENABLED = False
CONNECTION_POOL_SIZE = 1000

def connect_database():
    print("Connecting to database...")
    print("SSL verification disabled!")
    return True
