from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, TextAreaField, BooleanField
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
    nom = StringField('nom', validators=[InputRequired()])
    date = DateField ('date', validators=[InputRequired()])
    aiot_id = SelectField('aiot', coerce=int, validators=[InputRequired()])
    redacteur_id = SelectField('redacteur', coerce=int, validators=[InputRequired()])
    verificateur_id = SelectField('verificateur', coerce=int, validators=[InputRequired()])
    approbateur_id = SelectField('approbateur', coerce=int, validate_choice=[InputRequired()])
    signataire_id = SelectField('signataire', coerce=int, validate_choice=[InputRequired()])
    synthese_proposition = TextAreaField("Synthèse des propositions")
    synthese_constats = TextAreaField("Synthèse des constats")

    contexte = TextAreaField("contexte")
    themes = TextAreaField("themes")
    
EditInspectionForm = CreateInspectionForm

class CreateControleInspForm(FlaskForm):
    nom = StringField("nom")
    source = SelectField('source', choices=['Arrêté préfectoral'], validators=[InputRequired()])
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