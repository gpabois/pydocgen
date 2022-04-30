from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

import bcrypt

db = SQLAlchemy()
migrate = Migrate(compare_type=True)

class users(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    
    def __init__(email, password):
        self.email = email
        self.password = bcrypt.hashpw(password, bcrypt.gensalt( 12 ))
    
    def check_password(self, password):
        return bcrypt.checkpw(self.password, password)

class aiots(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    nom = db.Column('nom', db.String(255))
    numero_voie = db.Column(db.Integer)
    voie = db.Column(db.String(255))
    code_postal = db.Column(db.String(255))
    commune = db.Column(db.String(255))

    def __init__(self, nom, numero_voie, voie, code_postal, commune):
        self.nom = nom
        self.numero_voie = numero_voie
        self.voie = voie
        self.code_postal = code_postal
        self.commune = commune
        
class inspections(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    aiot_id = db.Column(db.Integer, db.ForeignKey('aiots.id'), nullable=False)
    aiot = db.relationship('aiots', backref=db.backref('inspections', lazy=True))
    nom = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __init__(self, nom, date, aiot_id):
        self.nom = nom
        self.date = date
        self.aiot_id = aiot_id

    def __repr__(self):
        return '<Inspection %r>' % self.nom
        
class insp_controles(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    insp_id = db.Column(db.Integer, db.ForeignKey('inspections.id'), nullable=False)
    inspection = db.relationship('inspections', backref=db.backref('controles', lazy=True))
    source = db.Column(db.String(255))
    date_source = db.Column(db.Date)
    article_source = db.Column(db.String(255))
    theme = db.Column(db.String(255))
    sous_theme = db.Column(db.String(255))
    prescription = db.Column(db.Text)
    constats = db.Column(db.Text)
    
    def __init__(self, insp_id, source, date_source, article_source, theme, sous_theme, prescription, constats):
        self.insp_id = insp_id
        self.source = source
        self.date_source = date_source
        self.article_source = article_source
        self.theme = theme
        self.sous_theme = sous_theme
        self.prescription = prescription
        self.constats = constats

class files(db.Model):
    id          = db.Column('id', db.Integer, primary_key = True)
    file_id     = db.Column(db.Text)
    store_id    = db.Column(db.Text)
    store_path  = db.Column(db.Text)
    
    def __init__(self, file_id, store_id, store_path):
        self.file_id = file_id
        self.store_id = store_id
        self.store_path = store_path        
