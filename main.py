from fastapi import FastAPI, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from models import Centra as DBCentra, Delivery as DBDelivery, Batch as DBBatch, Notification as DBNotification, SessionLocal
from schemas import CentraCreate, Centra, DeliveryCreate, Delivery, BatchCreate, Batch, DeliveryUpdate, NotificationCreate, Notification
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import crud  # Ensure this import is correct and points to your crud module

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific origins you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BatchUpdate(BaseModel):
    step: str
    weight: int

# In-memory storage for today's leaves weight
today_leaves_weight = 0

@app.get('/')
async def title():
    return "MORALM BACKEND"

@app.put("/batches/update_status", response_model=List[int])
def update_batches_status(batch_ids: List[int], db: Session = Depends(get_db)):
    batches = db.query(DBBatch).filter(DBBatch.Batch_ID.in_(batch_ids)).all()
    if not batches:
        raise HTTPException(status_code=404, detail="Batches not found")
    for batch in batches:
        batch.Status = "Warehouse"
    db.commit()
    return [batch.Batch_ID for batch in batches]

@app.get("/api/batches/{centra_id}", response_model=List[Batch])
def get_batches_by_centra(centra_id: int, db: Session = Depends(get_db)):
    batches = crud.get_batches_by_centra_id(db, centra_id=centra_id)
    if not batches:
        raise HTTPException(status_code=404, detail="Batches not found")
    return batches

@app.get("/api/weights")
def get_weights(centra_id: int, db: Session = Depends(get_db)):
    weights = crud.get_weights_by_centra_id(db, centra_id=centra_id)
    return weights

@app.get("/api/batches")
def get_batches(centra_id: int, db: Session = Depends(get_db)):
    batches = crud.get_batches_by_centra_id(db, centra_id=centra_id)
    return batches

@app.post("/centra/", response_model=Centra)
def create_centra(centra: CentraCreate, db: Session = Depends(get_db)):
    db_centra = DBCentra(**centra.dict())
    db.add(db_centra)
    db.commit()
    db.refresh(db_centra)
    return db_centra

@app.get("/centra/", response_model=List[Centra])
def read_centras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DBCentra).offset(skip).limit(limit).all()

@app.get("/centra/{centra_id}", response_model=Centra)
def read_centra(centra_id: int, db: Session = Depends(get_db)):
    db_centra = db.query(DBCentra).filter(DBCentra.Centra_ID == centra_id).first()
    if db_centra is None:
        raise HTTPException(status_code=404, detail="Centra not found")
    return db_centra

@app.put("/centra/{centra_id}", response_model=Centra)
def update_centra(centra_id: int, centra: CentraCreate, db: Session = Depends(get_db)):
    db_centra = db.query(DBCentra).filter(DBCentra.Centra_ID == centra_id).first()
    if db_centra is None:
        raise HTTPException(status_code=404, detail="Centra not found")
    for key, value in centra.dict().items():
        setattr(db_centra, key, value)
    db.commit()
    db.refresh(db_centra)
    return db_centra

@app.delete("/centra/{centra_id}", response_model=Centra)
def delete_centra(centra_id: int, db: Session = Depends(get_db)):
    db_centra = db.query(DBCentra).filter(DBCentra.Centra_ID == centra_id).first()
    if db_centra is None:
        raise HTTPException(status_code=404, detail="Centra not found")
    db.delete(db_centra)
    db.commit()
    return db_centra

@app.post("/delivery/", response_model=Delivery)
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    db_delivery = DBDelivery(**delivery.dict())
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery

@app.get("/delivery/", response_model=List[Delivery])
def read_deliveries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DBDelivery).offset(skip).limit(limit).all()

@app.get("/delivery/{package_id}", response_model=Delivery)
def read_delivery(package_id: int, db: Session = Depends(get_db)):
    db_delivery = db.query(DBDelivery).filter(DBDelivery.Package_ID == package_id).first()
    if db_delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return db_delivery

@app.put("/delivery/{package_id}", response_model=Delivery)
def update_delivery(package_id: int, delivery: DeliveryUpdate, db: Session = Depends(get_db)):
    db_delivery = db.query(DBDelivery).filter(DBDelivery.Package_ID == package_id).first()
    if db_delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    for key, value in delivery.dict(exclude_unset=True).items():
        setattr(db_delivery, key, value)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery

@app.delete("/delivery/{package_id}", response_model=Delivery)
def delete_delivery(package_id: int, db: Session = Depends(get_db)):
    db_delivery = db.query(DBDelivery).filter(DBDelivery.Package_ID == package_id).first()
    if db_delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    db.delete(db_delivery)
    db.commit()
    return db_delivery

@app.post("/batch/", response_model=Batch)
def create_batch(batch: BatchCreate, db: Session = Depends(get_db)):
    db_batch = DBBatch(**batch.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

@app.get("/batch/", response_model=List[Batch])
def read_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DBBatch).offset(skip).limit(limit).all()

@app.get("/batch/{batch_id}", response_model=Batch)
def read_batch(batch_id: int, db: Session = Depends(get_db)):
    db_batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if db_batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return db_batch

@app.get("/batch/package/{package_id}", response_model=Batch)
def read_batch_by_package(package_id: int, db: Session = Depends(get_db)):
    db_batch = db.query(DBBatch).filter(DBBatch.Package_ID == package_id).first()
    if db_batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return db_batch

@app.get("/centra/batch/{batch_id}", response_model=Centra)
def read_centra_by_batch(batch_id: int, db: Session = Depends(get_db)):
    db_batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if db_batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    db_centra = db.query(DBCentra).filter(DBCentra.Centra_ID == db_batch.Centra_ID).first()
    if db_centra is None:
        raise HTTPException(status_code=404, detail="Centra not found")
    return db_centra

@app.put("/batch/{batch_id}", response_model=Batch)
def update_batch(batch_id: int, batch_update: BatchUpdate, db: Session = Depends(get_db)):
    db_batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if db_batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Update the weight and status based on the step
    if batch_update.step == 'Wet Leaves':
        db_batch.WetWeight = batch_update.weight
        db_batch.Status = 'Wet Leaves'
    elif batch_update.step == 'Dry Leaves':
        db_batch.DryWeight = batch_update.weight
        db_batch.Status = 'Dry Leaves'
    elif batch_update.step == 'Flour Leaves':
        db_batch.PowderWeight = batch_update.weight
        db_batch.Status = 'Flour Leaves'
    elif batch_update.step == 'Rescale':
        db_batch.Status = 'Rescale'
        db_batch.WeightRescale = batch_update.weight

    # Create notification
    notification = DBNotification(
        title=f"Batch {batch_id} status changed",
        message=f"Batch {batch_id} status changed to {db_batch.Status}",
        timestamp=datetime.now()
    )
    db.add(notification)

    db.commit()
    db.refresh(db_batch)
    return db_batch

@app.delete("/batch/{batch_id}", response_model=Batch)
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    db_batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if db_batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    db.delete(db_batch)
    db.commit()
    return db_batch

@app.post("/api/create_batch", response_model=Batch)
def create_new_batch(weight: int, centra_id: int, db: Session = Depends(get_db)):
    new_batch = DBBatch(
        RawWeight=weight,
        InTimeRaw=datetime.now(),
        Centra_ID=centra_id,
        Status='Gather Leaves'
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch

@app.get("/api/archived_batches", response_model=List[Batch])
def get_archived_batches(db: Session = Depends(get_db)):
    archived_batches = db.query(DBBatch).filter(DBBatch.Status == "Archived").all()
    return archived_batches

@app.get("/api/notifications", response_model=List[Notification])
def get_notifications(db: Session = Depends(get_db)):
    notifications = db.query(DBNotification).order_by(DBNotification.timestamp.desc()).all()
    return notifications

@app.delete("/api/notifications/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(DBNotification).filter(DBNotification.id == notification_id).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted successfully"}

@app.delete("/api/notifications")
def delete_all_notifications(db: Session = Depends(get_db)):
    db.query(DBNotification).delete()
    db.commit()
    return {"message": "All notifications deleted successfully"}

@app.get("/api/warehouse_batches", response_model=List[Batch])
def get_warehouse_batches(db: Session = Depends(get_db)):
    warehouse_batches = db.query(DBBatch).filter(DBBatch.Status == "Warehouse").all()
    return warehouse_batches

@app.post("/add_leaves/", response_model=dict)
def add_leaves(weight: int = Body(...)):
    global today_leaves_weight
    today_leaves_weight += weight
    return {"message": "Leaves weight added", "today_leaves_weight": today_leaves_weight}

@app.get("/reset_leaves_weight/")
def reset_leaves_weight():
    global today_leaves_weight
    today_leaves_weight = 0
    return {"message": "Leaves weight reset"}

@app.get("/weekly_raw_weight/", response_model=List[dict])
def weekly_raw_weight(db: Session = Depends(get_db)):
    today = datetime.today()
    last_seven_days = [today - timedelta(days=i) for i in range(7)]
    weights = []
    for day in last_seven_days:
        weight = db.query(DBBatch.RawWeight).filter(DBBatch.InTimeRaw.between(day, day + timedelta(days=1))).sum()
        weights.append({"date": day.strftime("%Y-%m-%d"), "weight": weight or 0})
    return weights

@app.post("/create_batch/", response_model=Batch)
def create_batch(db: Session = Depends(get_db)):
    global today_leaves_weight
    new_batch = DBBatch(
        RawWeight=today_leaves_weight,
        InTimeRaw=datetime.now(),
        Status="Gather Leaves",
        Centra_ID=1  # Assuming a default Centra_ID, modify as needed
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    today_leaves_weight = 0  # Reset the in-memory storage after creating a batch
    return new_batch

@app.get("/centra_location/{centra_id}", response_model=str)
def get_centra_location(centra_id: int, db: Session = Depends(get_db)):
    centra = db.query(DBCentra).filter(DBCentra.Centra_ID == centra_id).first()
    if centra is None:
        raise HTTPException(status_code=404, detail="Centra not found")
    return centra.CentraName

@app.get("/gather_leaves_weight/{batch_id}", response_model=dict)
def gather_leaves_weight(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return {"RawWeight": batch.RawWeight, "InTimeRaw": batch.InTimeRaw}

@app.post("/start_process/{batch_id}/{step}", response_model=dict)
def start_process(batch_id: int, step: str, db: Session = Depends(get_db)):
    batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    current_time = datetime.now()
    if step == "wet":
        batch.InTimeWet = current_time
    elif step == "dry":
        batch.InTimeDry = current_time
    elif step == "powder":
        batch.InTimePowder = current_time
    else:
        raise HTTPException(status_code=400, detail="Invalid step")
    db.commit()
    db.refresh(batch)
    return {"message": "Process started", "InTime": current_time}

@app.post("/complete_process/{batch_id}/{step}", response_model=dict)
def complete_process(batch_id: int, step: str, weight: int = Body(...), db: Session = Depends(get_db)):
    batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    current_time = datetime.now()
    if step == "wet":
        batch.OutTimeWet = current_time
        batch.WetWeight = weight
        batch.Status = "Wet Leaves"
    elif step == "dry":
        batch.OutTimeDry = current_time
        batch.DryWeight = weight
        batch.Status = "Dry Leaves"
    elif step == "powder":
        batch.OutTimePowder = current_time
        batch.PowderWeight = weight
        batch.Status = "Powder Leaves"
    else:
        raise HTTPException(status_code=400, detail="Invalid step")
    db.commit()
    db.refresh(batch)
    return {"message": "Process completed", "OutTime": current_time, "Weight": weight}

@app.get("/batch_details/{batch_id}", response_model=dict)
def batch_details(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return {
        "Batch_ID": batch.Batch_ID,
        "RawWeight": batch.RawWeight,
        "InTimeRaw": batch.InTimeRaw,
        "InTimeWet": batch.InTimeWet,
        "OutTimeWet": batch.OutTimeWet,
        "WetWeight": batch.WetWeight,
        "InTimeDry": batch.InTimeDry,
        "OutTimeDry": batch.OutTimeDry,
        "DryWeight": batch.DryWeight,
        "InTimePowder": batch.InTimePowder,
        "OutTimePowder": batch.OutTimePowder,
        "PowderWeight": batch.PowderWeight,
        "Status": batch.Status
    }

@app.delete("/batch/{batch_id}", response_model=dict)
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    db.delete(batch)
    db.commit()
    return {"message": "Batch deleted"}

@app.post("/deliver_batches/", response_model=dict)
def deliver_batches(batch_ids: List[int], expedition: str, db: Session = Depends(get_db)):
    new_delivery = DBDelivery(
        Status="Pending",
        InDeliveryTime=datetime.now(),
        ExpeditionType=expedition
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    for batch_id in batch_ids:
        batch = db.query(DBBatch).filter(DBBatch.Batch_ID == batch_id).first()
        if batch is not None:
            batch.Package_ID = new_delivery.Package_ID
            batch.Status = "Deliver"
            db.commit()
    return {"message": "Batches delivered", "Package_ID": new_delivery.Package_ID}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
