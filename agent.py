from fastapi import Depends



from google import genai

from google.genai import types
import requests
from sqlalchemy import Date
from sqlalchemy.orm import Session

try:
    from .models import models
    from .config import settings
except ImportError:
    from models import models
    from config import settings

from sqlalchemy import cast, func, Date

from datetime import date



def Agent(db: Session):
    client1 = genai.Client(api_key=settings.GEMINI_APIKEY)

    
    
    posts = db.query(models.Post).filter(
    cast(models.Post.date, Date) == date.today()).all()
  
    for p in posts:
       if(p.etat==''):
           response1 = client1.models.generate_content(
              model='gemini-2.5-flash', 
              contents= "give me one caption example  to a facebook post as described ,only the paragraph "+p.description
          )
           generated_text =response1.text 
           
        
           cl = db.query(models.Client).filter(models.Client.id == p.idClient).first()
        
           timestamp_publication =p.date
        
      
           post_url = f'https://graph.facebook.com/v25.0/{cl.pageId}/feed'
           payload = {
            'message': generated_text,
            'access_token': cl.accessToken,
            "instagram_crossposting_eligible": True,
            'published': 'false',  
            'scheduled_publish_time': timestamp_publication
         }
           
           try:
            r = requests.post(post_url, data=payload)
            data = r.json()
            
            if 'id' in data:
                print(f"Successfully scheduled post for Client {cl.id}. Post ID: {data['id']}")
                p.etat="published"
            else:
                print(f"Failed to schedule post. FB Error: {data}")
                p.etat="unpublished"
                
           except requests.exceptions.RequestException as e:
             print(f"HTTP Request failed: {e}")
           
           db.commit()
         
           
    client1.close()
    