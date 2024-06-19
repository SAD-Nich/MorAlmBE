from sqlalchemy.orm import Session
import models  # Change this line from relative to absolute import

def get_weights_by_centra_id(db: Session, centra_id: int):
    return db.query(models.Weight).filter(models.Weight.centra_id == centra_id).all()

def get_batches_by_centra_id(db: Session, centra_id: int):
    return db.query(models.Batch).filter(models.Batch.Centra_ID == centra_id).all()

def create_notification(db: Session, title: str, message: str):
    notification = models.Notification(title=title, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_notifications(db: Session):
    return db.query(models.Notification).order_by(models.Notification.timestamp.desc()).all()