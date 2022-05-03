from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from functools import lru_cache
from itertools import chain

import bcrypt

db = SQLAlchemy()
migrate = Migrate(compare_type=True)

class users(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    reference = db.Column(db.String(255))
    fonction = db.Column(db.String(255))
    nom = db.Column(db.String(255))
    prenom = db.Column(db.String(255))
    telephone = db.Column(db.String(255))

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if 'password' in kwargs:
                password = kwargs['password']
                self.password = bcrypt.hashpw(password, bcrypt.gensalt( 12 ))
            else:
                setattr(self, k, v)
    
    def fullname(self):
        return "{} {}".format(self.nom, self.prenom)

    def check_password(self, password):
        return bcrypt.checkpw(self.password, password)

class aiots(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    nom = db.Column('nom', db.String(255))
    numero_voie = db.Column(db.Integer)
    voie = db.Column(db.String(255))
    code_postal = db.Column(db.String(255))
    commune = db.Column(db.String(255))

    code = db.Column(db.String(255))
    ied = db.Column(db.Boolean)
    synthese = db.Column(db.Text)
    email = db.Column(db.String(255))
    regime = db.Column(db.String(255))

    def __init__(self, nom, numero_voie, voie, code_postal, commune):
        self.nom = nom
        self.numero_voie = numero_voie
        self.voie = voie
        self.code_postal = code_postal
        self.commune = commune
    
    def fullvoie(self):
        if self.numero_voie:
            return "{} {}".format(self.numero_voie, self.voie)
        else:
            return self.voie
        
class inspections(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    aiot_id = db.Column(db.Integer, db.ForeignKey('aiots.id', ondelete='CASCADE'), nullable=False)
    aiot = db.relationship('aiots', backref=db.backref('inspections', lazy=True))
    nom = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)

    contexte = db.Column(db.Text)
    themes = db.Column(db.Text)

    synthese_proposition = db.Column(db.Text)
    synthese_constats = db.Column(db.Text)

    redacteur_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    redacteur = db.relationship('users', foreign_keys=[redacteur_id])
    
    verificateur_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verificateur = db.relationship('users', foreign_keys=[verificateur_id])
    
    approbateur_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approbateur = db.relationship('users', foreign_keys=[approbateur_id])

    signataire_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    signataire = db.relationship('users', foreign_keys=[signataire_id])

    def __repr__(self):
        return '<Inspection %r>' % self.nom

    def formatted_date(self):
        return self.date.strftime("%d/%m/%Y")

    def verificateur_est_approbateur(self):
        return self.verificateur_id == self.approbateur_id

    @lru_cache
    def controles_susceptibles_de_suites(self):
        return list(
            filter(
                lambda ctrl: ctrl.types_de_suites() == "Susceptibles de suites",
                self.controles
            )
        )
    
    @lru_cache
    def controles_sans_suites(self):
        return list(
            filter(
                lambda ctrl: ctrl.types_de_suites() == "Sans suites",
                self.controles
            )
        )        

    @lru_cache
    def demandes_exploitant(self):
        return list(
            chain.from_iterable(map(lambda ctrl: ctrl.demandes_exploitant(), self.controles))
        )

class insp_controles(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    insp_id = db.Column(db.Integer, db.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False)
    inspection = db.relationship('inspections', backref=db.backref('controles', lazy=True))
    source = db.Column(db.String(255))
    date_source = db.Column(db.Date)
    article_source = db.Column(db.String(255))
    theme = db.Column(db.String(255))
    sous_theme = db.Column(db.String(255))
    nom = db.Column(db.String(255))
    prescription = db.Column(db.Text)
    constats = db.Column(db.Text)

    @lru_cache
    def demandes_exploitant(self):
        return list(filter(lambda d: d, list(map(lambda rel: rel.demande_exploitant, self.demande_exploitant_rels))))

    def types_de_suites(self):
        if self.demandes_exploitant():
            return "Susceptibles de suites"
        else:
            return "Sans suites"
    
    def propositions_de_suites(self):
        return "Sans objet"

class insp_controles_demandes_exploitant(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    ctrl_id = db.Column(db.Integer, db.ForeignKey('insp_controles.id', ondelete='CASCADE'), nullable=False)
    ctrl = db.relationship('insp_controles', backref=db.backref('demande_exploitant_rels', lazy=True))
    demande_exploitant_id = db.Column(db.Integer, db.ForeignKey('demandes_exploitant.id', ondelete='CASCADE'), nullable=False)
    demande_exploitant = db.relationship('demandes_exploitant')

    def __init__(self, ctrl_id, demande_exploitant_id):
        self.ctrl_id = ctrl_id
        self.demande_exploitant_id = demande_exploitant_id

class demandes_exploitant(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)

    delai = db.Column(db.String(255))
    unite_delai = db.Column(db.String(255))
    contenu = db.Column(db.String(255))

    def __str__(self):
        return "{}, sous un délai de {} {}".format(self.contenu, self.delai, self.unite_delai)

class files(db.Model):
    id          = db.Column('id', db.Integer, primary_key = True)
    file_id     = db.Column(db.Text)
    store_id    = db.Column(db.Text)
    store_path  = db.Column(db.Text)
    
    def __init__(self, file_id, store_id, store_path):
        self.file_id = file_id
        self.store_id = store_id
        self.store_path = store_path        
