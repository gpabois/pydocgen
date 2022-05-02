from flask import Flask, session
from flask_login import login_user, login_required, logout_user, current_user

from .forms  import LoginForm, RegisterUserForm, CreateAiotForm, CreateInspectionForm, CreateControleInspForm
from .forms  import CreateUserForm, CreateDemandeExploitant
from .forms  import EditInspectionForm, EditControleInspForm, EditAiotForm
from .models import db, users, aiots, inspections, insp_controles, insp_controles_demandes_exploitant
from .models import demandes_exploitant
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
    import re
    from jinja2 import pass_eval_context
    from markupsafe import Markup, escape

    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    app.jinja_env.globals.update(enumerate=enumerate)

    @app.template_filter('nl2br')
    def nl2br(value):
        result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br>\n'))
                            for p in _paragraph_re.split(escape(value)))
        result = Markup(result)
        return result

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

    @app.route('/users/<int:id>')
    def show_user(id):
        user = users.query.get(id)
        return render_template("show_user.html", user=user)

    @app.route('/users/create', methods=['GET', 'POST'])
    def create_user():
        form = CreateUserForm()

        if form.validate_on_submit():
            user = users(
                email=form.email.data, 
                nom=form.nom.data, 
                prenom=form.prenom.data, 
                fonction=form.fonction.data, 
                reference=form.reference.data, 
                telephone=form.telephone.data
            )

            db.session.add(user)
            db.session.commit()
            return redirect(url_for("show_user", id=user.id))
        
        return render_template("create_user.html", form=form)

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

    @app.route('/aiots/<int:id>/edit', methods=['GET', 'POST'])    
    def edit_aiot(id):
        aiot = aiots.query.get(id)
        form = EditAiotForm(obj=aiot)
        
        if form.validate_on_submit():
            form.populate_obj(aiot)
            db.session.add(aiot)
            db.session.commit()
            return redirect(url_for('show_aiot', id=aiot.id))

        return render_template('edit_aiot.html', form=form)

    @app.route('/inspections/<int:id>/edit', methods=['GET', 'POST'])    
    def edit_inspection(id):
        inspection = inspections.query.get(id)
        form = EditInspectionForm(obj=inspection)
        
        form.aiot_id.choices = list(map(lambda aiot: (aiot.id, aiot.nom), aiots.query.all()))
        form.approbateur_id.choices = form.verificateur_id.choices = form.redacteur_id.choices = list(map(lambda user: (user.id, user.fullname()), users.query.all()))
        
        if form.validate_on_submit():
            form.populate_obj(inspection)
            db.session.add(inspection)
            db.session.commit()
            return redirect(url_for('show_inspection', id=inspection.id))

        return render_template('edit_inspection.html', form=form)

    @app.route('/aiots/<int:aiot_id>/inspections/create', methods=['GET', 'POST'])
    def create_inspection(aiot_id):
        form = CreateInspectionForm()
        
        form.aiot_id.choices = list(map(lambda aiot: (aiot.id, aiot.nom), aiots.query.all()))
        form.aiot_id.data = aiot_id
        form.approbateur_id.choices = form.verificateur_id.choices = form.redacteur_id.choices = list(map(lambda user: (user.id, user.fullname()), users.query.all()))
        
        if form.validate_on_submit():
            inspection = inspections()
            form.populate_obj(inspection)
            db.session.add(inspection)
            db.session.commit()
            return redirect(url_for('show_inspection', id=inspection.id))

        return render_template('create_inspection.html', form=form)

    @app.route('/inspections/<int:id>', methods=['GET'])
    def show_inspection(id):
        return render_template('show_inspection.html', inspection=inspections.query.get(id))

    @app.route('/inspections/<int:id>/be/exploitant/generate', methods=['GET'])
    def generate_inspection_be_exploitant(id):
        from . import docgen

        inspection = inspections.query.get(id)
        stream = docgen.generate_inspection_be_exploitant(inspection)

        file_name = "{}_{}_{}_{}.odt".format(
            inspection.date.strftime("%Y%m%d"),
            inspection.aiot.commune,
            inspection.aiot.nom,
            "Bordereau_exploitant"
        )
        return send_file(stream, download_name=file_name, mimetype='application/vnd.oasis.opendocument.text')

    @app.route('/inspections/<int:id>/rapport/generate', methods=['GET'])
    def generate_inspection_rapport(id):
        from . import docgen

        inspection = inspections.query.get(id)
        stream = docgen.generate_inspection_rapport(inspection)

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
            controle = insp_controles()
            controle.insp_id = inspection_id
            form.populate_obj(controle)
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

    @app.route('/inspections/controles/<int:ctrl_id>/demandes_exploitant/create', methods=['GET', 'POST'])
    def create_insp_ctrl_demande_exploitant(ctrl_id):
        form = CreateDemandeExploitant()
        ctrl = insp_controles.query.get(ctrl_id)

        if form.validate_on_submit():
            demande_exploitant = demandes_exploitant()
            form.populate_obj(demande_exploitant)
            db.session.add(demande_exploitant)
            db.session.flush()
            db.session.refresh(demande_exploitant)
            db.session.add(
                insp_controles_demandes_exploitant(
                    ctrl_id,
                    demande_exploitant.id
                )
            )
            db.session.commit()
            return redirect(url_for('show_inspection', id=ctrl.insp_id))

        return render_template("create_demande_exploitant.html", form=form)
    
    @app.route('/demandes_exploitant/<int:id>', methods=['GET'])
    def delete_demande_exploitant(id):
        demande = demandes_exploitant.query.get(id)
        db.session.delete(demande)
        db.session.commit()

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index'))
