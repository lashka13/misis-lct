from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class Sentiment(enum.Enum):
    POSITIVE = "положительно"
    NEGATIVE = "отрицательно"
    NEUTRAL = "нейтрально"


class ReviewTopic(Base):
    """
    Association table linking reviews and topics.
    Each pair (review, topic) has exactly one sentiment.
    """

    __tablename__ = "review_topics"

    review_id = Column(
        Integer, ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True
    )
    topic_id = Column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True
    )
    sentiment = Column(
        Enum(Sentiment, name="sentiment", create_type=False), nullable=False
    )

    # ORM relationships
    review = relationship("Review", back_populates="review_topics")
    topic = relationship("Topic", back_populates="review_topics")

    __table_args__ = (
        UniqueConstraint("review_id", "topic_id", name="uq_review_topic"),
        Index("ix_review_topics_review", "review_id"),
        Index("ix_review_topics_topic", "topic_id"),
        Index("ix_review_topics_sentiment", "sentiment"),
    )


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    rating = Column(Integer, nullable=True)

    # link to association
    review_topics = relationship(
        "ReviewTopic", back_populates="review", cascade="all, delete-orphan"
    )
    topics = relationship("Topic", secondary="review_topics", back_populates="reviews")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True, index=True)

    # link to association
    review_topics = relationship(
        "ReviewTopic", back_populates="topic", cascade="all, delete-orphan"
    )
    reviews = relationship("Review", secondary="review_topics", back_populates="topics")
