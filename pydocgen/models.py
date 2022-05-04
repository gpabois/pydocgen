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
    
    def formatted_voie(self):
        return self.fullvoie()

    def fullvoie(self):
        if self.numero_voie:
            return "{} {}".format(self.numero_voie, self.voie)
        else:
            return self.voie

class arretes(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    aiot_id = db.Column(db.Integer, db.ForeignKey('aiots.id', ondelete='CASCADE'), nullable=False)
    aiot = db.relationship('aiots', backref=db.backref('arretes', lazy=True))

    nature = db.Column(db.String(255))
    
    visas = db.Column(db.Text)
    considerants = db.Column(db.Text)

    def get_visas(self):
        return self.visas.split(";;")
    
    def get_considerants(self):
        return self.considerants.split(";;")

    def get_titre(self):
        return "portant réglementation complémentaire d'installation classées pour la protection de l'environnement exploitée " + \
            "par la société {} sise {} à {}".format(aiot.nom, aiot.formatted_voie(), aiot.commune)

class articles(db.Model):
    id = db.Column('id', db.Integer, primary_key = True) 
    order = db.Column(db.Integer)
    arrete_id = db.Column(db.Integer, db.ForeignKey('arretes.id', ondelete='CASCADE'), nullable=False)
    arrete = db.relationship('arretes', backref=db.backref('articles', lazy=True))

    nom = db.Column(db.String(255))

    def get_titre(self):
        return "Article {}{}".format(order, ": {}".format(self.nom) if self.nom else "")

    @lru_cache
    def get_dispositions(self):
        return list(chain(*[
            dispositions_abrogatoires.query.filter_by(article_id=self.id).all(),
            dispositions_autres.query.filter_by(article_id=self.id).all()
        ]))

    def get_contenu(self):
        list(map(str, self.get_dispositions())).join("\n\n")

class dispositions_autres(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)   
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)

    contenu = db.Column(db.Text)

    def __str__(self):
        return self.contenu

class dispositions_abrogatoires(db.Model):
    id = db.Column('id', db.Integer, primary_key = True) 
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    
    nom_arrete = db.Column(db.String(255), nullable=False)
    articles = db.Column(db.Text, nullable=True)

    def __str__(self):
        if self.articles:
            "Les dispositions prévues aux articles {} de l'{} sont abrogées."
        else:
            "Les dispositions prévues de l'{} sont abrogées."

class inspections_arretes_rel(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    arrete_id = db.Column(db.Integer, db.ForeignKey('arretes.id', ondelete='CASCADE'), nullable=False)
    arrete = db.relationship('inspections', backref=db.backref('arretes_rel', lazy=True))
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False)
    inspection = db.relationship('arretes', backref=db.backref('inspections_rel', lazy=True))

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
