

import datetime
import io

from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, File, HTTPException,Request, UploadFile
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from starlette import status
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

try:
    from .agent import Agent
    from .database import get_db
    from .models import models, schemas
except ImportError:
    from agent import Agent
    from database import get_db
    from models import models, schemas

import pandas as pd
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://marketing-agent2.vercel.app",
                   "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
scheduler = BackgroundScheduler()
scheduler.start()

@app.post("/connect",response_model=schemas.ConnectAdmin)
async def connect_admin(request:Request,db:Session =Depends(get_db)):
    try:
        data = await request.json()
        
        admin = db.query(models.Administrateur).filter(models.Administrateur.email == data.get("email")).first()
        
        if admin and check_password_hash(admin.mdp,data.get("mdp")):
            return {"connected": True}
        else:
            return {"connected": False}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/upload")
async def upload_file(file:UploadFile=File(...), status_code=status.HTTP_201_CREATED,db:Session =Depends(get_db)):
    content = await file.read()
    df = pd.read_excel(io.BytesIO(content))
    
    # Normalise les noms de colonnes : enlève les espaces, met en minuscule
    df.columns = df.columns.str.strip().str.lower()
    print("Colonnes détectées:", df.columns.tolist())  # debug temporaire
    
    email_recherche = str(df.at[0, 'emailclient']).strip()
    client = db.query(models.Client).filter(models.Client.email == email_recherche).first()
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun client trouvé avec l'email '{email_recherche}'"
        )
    
    idClient = client.id
    
    for i in range(0, len(df)):
        date = df.at[i, 'date']
        description = df.at[i, 'description']
        
        new_post = models.Post(description=description, date=date, idClient=idClient)
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
    
    end_date = datetime.now() + timedelta(days=90)
    
    scheduler.add_job(
        Agent,
        trigger='cron',
        hour=1,
        minute=0,
        args=[db],
        end_date=end_date,
        id=email_recherche
    )
    
    return "done"

@app.post("/cancel/{emailclient}")
def cancel_job(emailclient: str, db: Session = Depends(get_db)):
    try:
        scheduler.remove_job(emailclient)
    except JobLookupError:
        pass  

    client = db.query(models.Client).filter(models.Client.email == emailclient).first()
    if client:
        db.query(models.Post).filter(models.Post.idClient == client.id).update({"etat": "annulé"})
        db.commit()

    return "done"

@app.post("/cancel-post/{post_id}")
def cancel_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail=f"Aucun post trouvé avec l'id {post_id}")
    
    post.etat = "annulé"
    db.commit()
    
    return "done"

@app.get("/clients/count")
def get_clients_count(db: Session = Depends(get_db)):
    return {"count": db.query(models.Client).count()}

@app.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.date.desc()).all()
    result = []
    for post in posts:
        client = db.query(models.Client).filter(models.Client.id == post.idClient).first()
        result.append({
            "id": post.id,
            "emailclient": client.email if client else "",
            "nomClient": client.nom if client else "",
            "date": post.date.isoformat(),
            "description": post.description,
            "etat": post.etat
        })
    return result