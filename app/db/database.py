from app.core.config import MONGO_DETAILS
from motor.motor_asyncio import AsyncIOMotorClient


client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.learnify
# db = client["learnify"] # This is also valid