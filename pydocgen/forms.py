from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, TextAreaField, BooleanField,IntegerField
from wtforms.validators import InputRequired, Optional, EqualTo, Length, Email

from .models import aiots, users

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired()])
    
    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        users.query.filter_by(email=self.email.data).first()
    
        if not user or not user.check_password(self.password.data):
            self.email.errors.append('Email ou mot de passe invalide')
            return False
    
        self.user = user
        return True

class RegisterUserForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4), EqualTo('confirm_password')])
    confirm_password = PasswordField('confirm_password', validators=[Length(min=4)])

class CreateUserForm(FlaskForm):
    nom = StringField('nom')
    prenom = StringField('prenom')
    fonction = StringField('fonction')
    telephone = StringField('telephone')
    reference = StringField('reference')
    email = StringField('email', validators=[InputRequired(), Email()])

class CreateAiotForm(FlaskForm):
    nom = StringField('nom', validators=[InputRequired()])
    numero_voie = StringField('numero_voie', validators=[Optional()])
    voie = StringField('voie', validators=[Optional()])
    code_postal = StringField('code_postal', validators=[Optional()])
    commune = StringField('commune', validators=[InputRequired()])
    email = StringField("email", validators=[Optional(), Email()])
    regime = SelectField("regime", choices=["Autorisation", "Enregistrement", "Déclaration"])
    ied = BooleanField("ied")
    code = StringField("code")
    synthese = TextAreaField("synthese")

EditAiotForm = CreateAiotForm

class CreateInspectionForm(FlaskForm):
    nom = StringField('Nom', validators=[InputRequired()])
    date = DateField ('Date', validators=[InputRequired()])
    aiot_id = SelectField('AIOT', coerce=int, validators=[InputRequired()])
    redacteur_id = SelectField('Rédacteur', coerce=int, validators=[InputRequired()])
    verificateur_id = SelectField('Vérificateur', coerce=int, validators=[InputRequired()])
    approbateur_id = SelectField('Approbateur', coerce=int, validate_choice=[InputRequired()])
    signataire_id = SelectField('Signataire correspondance', coerce=int, validate_choice=[InputRequired()])
    synthese_proposition = TextAreaField("Synthèse des propositions")
    synthese_constats = TextAreaField("Synthèse des constats")

    contexte = TextAreaField("Contexte")
    themes = TextAreaField("Thémes")
    
EditInspectionForm = CreateInspectionForm

class CreateControleInspForm(FlaskForm):
    nom = StringField("nom")
    source = SelectField('source', choices=['Arrêté préfectoral', 'Code de l\'environnement'], validators=[InputRequired()])
    date_source = DateField('date_source', validators=[Optional()])
    article_source = StringField('article_source', validators=[InputRequired()])
    theme = StringField("theme", validators=[InputRequired()])
    sous_theme = StringField("sous_theme", validators=[InputRequired()])
    prescription = TextAreaField('prescription', validators=[InputRequired()])
    constats = TextAreaField('constats', validators=[Optional()])

EditControleInspForm = CreateControleInspForm

class CreateDemandeExploitant(FlaskForm):
    delai       = StringField('délai', validators=[InputRequired()])
    unite_delai = SelectField('unité_délai', choices=["jours", "mois"], validators=[InputRequired()])
    contenu     = TextAreaField("contenu")

class ReponseAvisPCForm(FlaskForm):
    date_envoi = DateField("Date d'envoi")
    date_reception = DateField("Date réception")
    date_depot = DateField("Date du dépôt")
    reference_pc = StringField("Référence du PC")
    synthese_projet = TextAreaField("Synthèse du projet")
    ancienne_icpe = TextAreaField("Ancienne ICPE (laisser vide si pas applicable)")
    status_pj = SelectField("Status des éléments fournis", choices=["pas_applicable", "absent", "irregulier", "conforme"])
    explication_status_pj = TextAreaField("Explication")
    avis = SelectField("Avis", choices=["defavorable", "favorable"])

class ArreteForm(FlaskForm):
    nature = SelectField("Nature", choices=[
        ("complementaire", "Arrêté complémentaire"),
        ("mesures_urgence", "Arrêté de mesures d'urgence"),
        ("levee_mesures_urgences", "Arrêté de levée de mesures d'urgences")
    ])

    aiot_id = SelectField('AIOT', coerce=int, validators=[InputRequired()])
    visas = TextAreaField('Visas (sans le VU)')
    considerants = TextAreaField('Considérants (sans le CONSIDERANT)')

CreateArreteForm = ArreteForm
EditArreteForm = ArreteForm

class ArticleForm(FlaskForm):
    order = IntegerField("Numéro")
    nom = StringField("Nom (optionnel)")

CreateArticleForm = ArticleForm
EditArticleForm = ArticleForm

class DispositionAbrogatoireForm(FlaskForm):
    nom_arrete = StringField("Nom de l'arrêté")
    articles = StringField("Articles à abroger (optionnel)")

CreateDispositionAbrogatoireForm = DispositionAbrogatoireForm
EditDispositionAbrogatoireForm = DispositionAbrogatoireForm

class DispositionAutreForm(FlaskForm):
    contenu = TextAreaField("Disposition")

CreateDispositionAutreForm = DispositionAutreForm
EditDispositionAutreForm = DispositionAutreForm