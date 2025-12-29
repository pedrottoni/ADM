from sqlmodel import Session
from core.database.models import User
import math

class GamificationEngine:
    @staticmethod
    def calculate_level(xp: int) -> int:
        """
        Calculate level based on XP.
        Formula: Level = floor(sqrt(XP / 100)) + 1
        Examples:
            0 XP -> Level 1
            100 XP -> Level 2
            400 XP -> Level 3
        """
        if xp < 0:
            return 1
        return math.floor(math.sqrt(xp / 100)) + 1

    @staticmethod
    def xp_for_next_level(current_level: int) -> int:
        """Calculate total XP needed to reach the NEXT level."""
        return ((current_level) ** 2) * 100

    @staticmethod
    def add_xp(user: User, amount: int, session: Session) -> User:
        """Adds XP to user and handles level up."""
        old_level = user.level
        user.xp += amount
        new_level = GamificationEngine.calculate_level(user.xp)
        
        if new_level > old_level:
            user.level = new_level
            # Future: Trigger Level Up Event/Notification
            print(f"🎉 LEVEL UP! User {user.username} is now Level {new_level}!")
            
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
