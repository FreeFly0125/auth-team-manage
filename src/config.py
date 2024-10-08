import os

VERSION = "1"

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")

REDIS = "redis:6379"
MONGO_ADDRESS = "mongodb://mongo:27017/"
MONGO = MONGO_ADDRESS + "bluquist_" + ENVIRONMENT
