from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.base import Base


class Player(Base):
    __tablename__ = "player"

    plr_id = Column(BigInteger, primary_key=True)
    rating = Column(Integer, default=1000)
    total_games = Column(Integer, default=0)

    join_date = Column(BigInteger)
    last_activity = Column(BigInteger)

    bjgames = relationship("BJGame", back_populates="player")


class BJGame(Base):
    __tablename__ = "bjgame"

    game_id = Column(Integer, primary_key=True)
    bet_amount = Column(Integer)
    result = Column(String(50), default="in_proccess")
    next_cards = Column(String)

    d_cards = Column(String)
    d_points = Column(Integer)

    p_id = Column(BigInteger, ForeignKey("player.plr_id"))
    p_cards = Column(String)
    p_points = Column(Integer)

    player = relationship("Player", back_populates="bjgames")
