from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# implement database model classes

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    timeavai = db.Column(db.String, nullable = False)
    contact = db.Column(db.String, nullable = False)
    talents = db.relationship("Talent", cascade = "delete")
    needs = db.relationship("Need", cascade = "delete") 

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
            "needs": [n.serialize() for n in self.needs]
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