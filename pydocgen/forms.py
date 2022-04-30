from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, TextAreaField
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

class CreateAiotForm(FlaskForm):
    nom = StringField('nom', validators=[InputRequired()])
    numero_voie = StringField('numero_voie', validators=[Optional()])
    voie = StringField('voie', validators=[Optional()])
    code_postal = StringField('code_postal', validators=[Optional()])
    commune = StringField('commune', validators=[InputRequired()])

class CreateInspectionForm(FlaskForm):
    nom = StringField('nom', validators=[InputRequired()])
    date = DateField ('date', validators=[InputRequired()])
    aiot_id = SelectField('aiot', coerce=int, validators=[InputRequired()])

UpdateInspectionForm = CreateInspectionForm

class CreateControleInspForm(FlaskForm):
    source = SelectField('source', choices=['Arrêté préfectoral'], validators=[InputRequired()])
    date_source = DateField('date_source', validators=[Optional()])
    article_source = StringField('article_source', validators=[InputRequired()])
    theme = StringField("theme", validators=[InputRequired()])
    sous_theme = StringField("sous_theme", validators=[InputRequired()])
    prescription = TextAreaField('prescription', validators=[InputRequired()])
    constats = TextAreaField('constats', validators=[InputRequired()])

EditControleInspForm = CreateControleInspForm