from flask import Flask, session
from flask_login import login_user, login_required, logout_user, current_user

from .forms import LoginForm, RegisterUserForm, CreateAiotForm, CreateInspectionForm, CreateControleInspForm
from .forms import EditControleInspForm
from .models import db, users, aiots, inspections, insp_controles
from .files  import store

import uuid

from urllib.parse import urlparse, urljoin
from flask import render_template, redirect, request, url_for, abort, send_file

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def init_app(app):
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/users/register', methods=['GET', 'POST'])
    def register_user():
        form = RegisterUserForm()
        
        if form.validate_on_submit():
            db.session.add(users(form.email.data, form.password.data))
            db.session.commit()
            return redirect(next or url_for('login'))
        
        return render_template('register_user.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            # Login and validate the user.
            # user should be an instance of your `User` class
            login_user(form.user)

            flash('Logged in successfully.')

            next = request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            if not is_safe_url(next):
                return abort(400)

            return redirect(next or url_for('index'))
            
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/aiots', methods=['GET', 'POST'])
    def list_aiots():
        return render_template('list_aiots.html', aiots=aiots.query.all())

    @app.route('/aiots/<int:id>', methods=['GET'])
    def show_aiot(id):
        return render_template('show_aiot.html', aiot=aiots.query.get(id))

    @app.route('/aiots/create', methods=['GET', 'POST'])
    def create_aiot():
        form = CreateAiotForm()
        
        if form.validate_on_submit():
            aiot = aiots(form.nom.data, form.numero_voie.data, form.voie.data, form.code_postal.data, form.commune.data)
            db.session.add(aiot)
            db.session.commit()

            return redirect(url_for('show_aiot', id=aiot.id))
        
        return render_template('create_aiot.html', form=form)  
            
    @app.route('/aiots/<int:aiot_id>/inspections/create', methods=['GET', 'POST'])
    def create_inspection(aiot_id):
        form = CreateInspectionForm()
        form.aiot_id.choices = list(map(lambda aiot: (aiot.id, aiot.nom), aiots.query.all()))
        
        if form.validate_on_submit():
            inspection = inspections(form.nom.data, form.date.data, form.aiot_id.data)
            db.session.add(inspection)
            db.session.commit()
            return redirect(url_for('show_inspection', id=inspection.id))

        return render_template('create_inspection.html', form=form)

    @app.route('/inspections/<int:id>', methods=['GET'])
    def show_inspection(id):
        return render_template('show_inspection.html', inspection=inspections.query.get(id))

    @app.route('/inspections/<int:id>/rapport/generate', methods=['GET'])
    def generate_inspection_rapport(id):
        from . import docgen

        inspection = inspections.query.get(id)
        stream = docgen.generate_rapport_inspection(inspection)

        file_name = "{}_{}_{}_{}.odt".format(
            inspection.date.strftime("%Y%m%d"),
            inspection.aiot.commune,
            inspection.aiot.nom,
            "Rapport_inspection"
        )
        return send_file(stream, download_name=file_name, mimetype='application/vnd.oasis.opendocument.text')


    @app.route('/inspections/<int:id>/delete', methods=['GET'])
    def delete_inspection(id):
        inspection = inspections.query.get(id)
        aiot_id = inspection.aiot_id
        db.session.delete(inspection)
        db.session.commit()
        return redirect(url_for('show_aiot', id=aiot_id))  

    @app.route('/inspections/<int:inspection_id>/controles/create', methods=['GET', 'POST'])
    def create_insp_controle(inspection_id):
        form = CreateControleInspForm()

        if form.validate_on_submit():
            controle = insp_controles(inspection_id, form.source.data, form.date_source.data, form.article_source.data, 
                form.theme.data, form.sous_theme.data, form.prescription.data, form.constats.data)
            db.session.add(controle)
            db.session.commit()
            return redirect(url_for('show_inspection', id=inspection_id))
        
        return render_template('create_insp_controle.html', form=form)

    @app.route('/inspections/controles/<int:id>/edit', methods=['GET', 'POST'])
    def edit_insp_controle(id):
        controle = insp_controles.query.get(id)
        form = EditControleInspForm(obj=controle)
        
        if form.validate_on_submit():
            form.populate_obj(controle)
            db.session.add(controle)
            db.session.commit()
            return redirect(url_for('show_inspection', id=controle.insp_id))
        
        return render_template('edit_insp_controle.html', form=form)

    @app.route('/inspections/controles/<int:id>/delete', methods=['GET'])
    def delete_insp_controle(id):
        controle = insp_controles.query.get(id)
        insp_id = controle.insp_id
        db.session.delete(controle)
        db.session.commit()
        return redirect(url_for('show_inspection', id=insp_id))
