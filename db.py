from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
import datetime
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ['png','gif','jpg','jpeg']
BASE_DIR = os.getcwd()
S3_BUCKET = 'sp2021hackchallenge'
S3_BASE_URL = f'http://{S3_BUCKET}.s3-us-east-2.amazonaws.com'

# implement database model classes

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    timeavai = db.Column(db.String, nullable = False)
    contact = db.Column(db.String, nullable = False)
    talents = db.relationship("Talent", cascade = "delete")
    needs = db.relationship("Need", cascade = "delete")
    asset = db.relationship("Asset", cascade = "delete")

    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.timeavai = ""
        self.contact = ""

    def serialize(self):
        # talents = []
        # needs = []
        # for talent in self.talents:
        #     talents.append(talent)
        # for need in self.needs:
        #     needs.append(need)

        return {
            "id ": self.id,
            "username": self.username,
            "timeavai": self.timeavai,
            "contact": self.contact,
            "talents": [t.serialize() for t in self.talents],
            "needs": [n.serialize() for n in self.needs],
            "profile_pic": [a.serialize() for a in self.asset]
        } 
    
    def check(self, user2):
        tmatch = False 
        nmatch = False

        for t in self.talents:
            if not tmatch:
                for n in user2.needs:
                    if t.talent == n.need:
                        tmatch = True
           
        for n in self.needs:
            if not nmatch:
                for t in user2.talents:
                    if n.need == t.talent:
                        nmatch = True 
                        
        if tmatch and nmatch:
            return 3
        elif tmatch:
            return 2
        elif nmatch:
            return 1
        else:
            return 0


class Talent(db.Model):
    __tablename__ = "talent"
    id = db.Column(db.Integer, primary_key = True)
    talent = db.Column(db.String, nullable = False)
    experience = db.Column(db.String, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        self.talent = kwargs.get("talent")
        self.experience = ""
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        return {
            "id": self.id,
            "talent": self.talent,
            "experience": self.experience,
            # "user_id": self.user_id
        }


class Need(db.Model):
    __tablename__ = "need"
    id = db.Column(db.Integer, primary_key = True)
    need = db.Column(db.String, nullable = False)
    issue = db.Column(db.String, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        self.need = kwargs.get("need")
        self.issue = ""
        self.user_id = kwargs.get("user_id")
    
    def serialize(self):
        return {
            "id": self.id,
            "need": self.need,
            "issue": self.issue
        }

class Asset(db.Model):
    __tablename__ = 'asset'

    id = db.Column(db.Integer, primary_key=True)
    base_url = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable = False)
    extension = db.Column(db.String, nullable = False)
    height = db.Column(db.Integer, nullable = False)
    width = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        self.create(kwargs.get('image_data'))
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at) 
        }
    
    def create(self, image_data):
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]
            if ext not in EXTENSIONS:
                raise Exception(f'Extension {ext} not supported!')

            salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(16))
            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.height = img.height
            self.width = img.width
            self.created_at = datetime.datetime.now()

            img_filename = f'{salt}.{ext}'
            self.upload(img, img_filename)

        except Exception as e:
            print('Error', e)

    def upload(self, img, img_filename):
        try:
            img_temploc = f'{BASE_DIR}/{img_filename}'
            img.save(img_temploc)

            s3_client = boto3.client('s3')
            s3_client.upload_file(img_temploc, S3_BUCKET, img_filename)

            s3_resource = boto3.resource('s3')
            object_acl = s3_resource.ObjectAcl(S3_BUCKET, img_filename)
            object_acl.put(ACL="public-read")
            os.remove(img_temploc)
            
        except Exception as e:
            print('Upload Failed:', e)