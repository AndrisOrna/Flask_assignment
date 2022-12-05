import requests
from base64 import b64encode

def retrieve_image(url):
    response = requests.get(url)
    base64img = "data:image/png;base64," \
        + b64encode(response.content).decode('ascii')
    return base64img

def db_add_one(item, db):
    try:
        db.session.add(item)
        db.session.commit()
        return None
    except:
        return 'There was an issue adding your car'

def db_add_multiple(items, db):
    for item in items:
        try:
            db.session.add(item)
        except:
            return 'There was an issue adding your cars, please add one by one'
    
    db.session.commit()
    return None