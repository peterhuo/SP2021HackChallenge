from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# implement database model classes

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    timeavai = db.Column(db.String, nullable = False)
    contact = db.Column(db.String, nullable = False)
    talents = relationship("Talent", cascade = "delete")
    needs = relationship("Need", cascade = "delete") 

    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.timeavai = ""
        self.contact = ""

    def serialize(self):
        talents = []
        needs = []
        for talent in self.talents:
            talents.append(talent)
        for need in self.needs:
            needs.append(need)

        return {
            "id ": self.id,
            "username": self.username,
            "timeavai": self.timeavai,
            "contact": self.contact,
            "talents": [t.serialize() for t in self.talents],
            "needs": [n.serialize() for n in self.needs]
        } 

class Talent(db.Model):
    __tablename__ = "talent"
    id = db.Column(db.Integer, primary_key = True)
    talent = db.Column(db.String, nullable = False)
    experience = db.Column(db.String, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        self.talent = kwargs.get("talent")
        self.experience = kwargs.get("experience")

    def serialize(self):
        return {
            "id": self.id,
            "talent": self.talent,
            "experience": self.experience
        }

class Need(db.Model):
    __tablename__ = "need"
    id = db.Column(db.Integer, primary_key = True)
    need = db.Column(db.String, nullable = False)
    issue = db.Column(db.String, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        self.need = kwargs.get("need")
        self.issue = kwargs.get("issue")
    
    def serialize(self):
        return {
            "id": self.id,
            "need": self.need.
            "issue": self.issue
        }