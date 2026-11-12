
# DEMO ONLY: Intentionally risky database configuration

# Critical database settings
DATABASE_HOST = "0.0.0.0"
DATABASE_PORT = 3306
DATABASE_NAME = "production_db"

# Security risks
DEBUG = True
SSL_ENABLED = False
ENCRYPTION_ENABLED = False
AUTHENTICATION_REQUIRED = False

# Performance risks
CONNECTION_POOL_SIZE = 1000
QUERY_TIMEOUT = 0
MAX_RETRIES = 100

# Backup and recovery risks
AUTO_BACKUP_ENABLED = False
ROLLBACK_ENABLED = False

# Logging risks
LOG_LEVEL = "DEBUG"
LOG_SENSITIVE_DATA = True

# Release status
ENVIRONMENT = "PRODUCTION"
