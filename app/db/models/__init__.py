# Import all models here to ensure SQLAlchemy finds them
from .user import User
from .station import Station # Assuming station.py exists based on User model
from .point import PointBalance, PointTransaction, PointRule
from .resv_reservation import ResvReservation
from .resv_chat import ResvChat # Add ResvChat import
# Import other models as needed

print("Models initialized")
