from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import config

engine       = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
Base         = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DetectionEvent(Base):
    __tablename__ = "detection_events"
    id            = Column(Integer, primary_key=True, index=True)
    event_type    = Column(String, nullable=False)
    label         = Column(String, nullable=False)
    confidence    = Column(Float,  nullable=False)
    camera_source = Column(String, nullable=False)
    snapshot_path = Column(String, default="")
    video_path    = Column(String, default="")
    timestamp     = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "event_type": self.event_type, "label": self.label,
            "confidence": self.confidence, "camera_source": self.camera_source,
            "snapshot_path": self.snapshot_path, "video_path": self.video_path,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

def init_db():
    Base.metadata.create_all(bind=engine)
