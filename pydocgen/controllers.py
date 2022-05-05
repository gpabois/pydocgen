from flask import Flask, session
from flask_login import login_user, login_required, logout_user, current_user

from .forms  import LoginForm, RegisterUserForm, CreateAiotForm, CreateInspectionForm, CreateControleInspForm
from .forms  import CreateUserForm, CreateDemandeExploitant
from .forms  import EditInspectionForm, EditControleInspForm, EditAiotForm
from .forms import ReponseAvisPCForm

from .models import db, users, aiots
from .models import demandes_exploitant

from .models import inspections, controles, controles_demandes_exploitant_rels
from .models import arretes, arretes_inspections_rels
from .forms import CreateArreteForm, EditArreteForm
from .models import articles
from .forms  import CreateArticleForm, EditArticleForm
from .models import dispositions_autres, dispositions_abrogatoires
from .forms import CreateDispositionAbrogatoireForm, EditDispositionAbrogatoireForm
from .forms import CreateDispositionAutreForm, EditDispositionAutreForm

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
        return redirect(url_for("list_aiots"))

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

    @app.route('/users/nouveau', methods=['GET', 'POST'])
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
        return render_template('aiots/list.html', aiots=aiots.query.all())

    @app.route('/aiots/<int:id>', methods=['GET'])
    def show_aiot(id):
        return render_template('aiots/show.html', aiot=aiots.query.get(id))

    @app.route('/aiots/nouveau', methods=['GET', 'POST'])
    def create_aiot():
        form = CreateAiotForm()
        
        if form.validate_on_submit():
            aiot = aiots(form.nom.data, form.numero_voie.data, form.voie.data, form.code_postal.data, form.commune.data)
            db.session.add(aiot)
            db.session.commit()

            return redirect(url_for('show_aiot', id=aiot.id))
        
        return render_template('aiots/create.html', form=form)  

    @app.route('/aiots/<int:id>/edit', methods=['GET', 'POST'])    
    def edit_aiot(id):
        aiot = aiots.query.get(id)
        form = EditAiotForm(obj=aiot)
        
        if form.validate_on_submit():
            form.populate_obj(aiot)
            db.session.add(aiot)
            db.session.commit()
            return redirect(url_for('show_aiot', id=aiot.id))

        return render_template('aiots/edit.html', form=form)

    @app.route('/inspections/<int:id>/edit', methods=['GET', 'POST'])    
    def edit_inspection(id):
        inspection = inspections.query.get(id)
        form = EditInspectionForm(obj=inspection)
        
        form.aiot_id.choices = list(map(lambda aiot: (aiot.id, aiot.nom), aiots.query.all()))
        form.signataire_id.choices = form.approbateur_id.choices = form.verificateur_id.choices = form.redacteur_id.choices = list(map(lambda user: (user.id, user.fullname()), users.query.all()))
        
        if form.validate_on_submit():
            form.populate_obj(inspection)
            db.session.add(inspection)
            db.session.commit()
            return redirect(url_for('show_inspection', id=inspection.id))

        return render_template('inspections/edit.html', form=form)

    @app.route('/aiots/<int:aiot_id>/inspections/nouveau', methods=['GET', 'POST'])
    def create_inspection(aiot_id):
        form = CreateInspectionForm()
        
        form.aiot_id.choices = list(map(lambda aiot: (aiot.id, aiot.nom), aiots.query.all()))
        form.aiot_id.data = aiot_id
        form.signataire_id.choices = form.approbateur_id.choices = form.verificateur_id.choices = form.redacteur_id.choices = list(map(lambda user: (user.id, user.fullname()), users.query.all()))
        
        if form.validate_on_submit():
            inspection = inspections()
            form.populate_obj(inspection)
            db.session.add(inspection)
            db.session.commit()
            return redirect(url_for('show_inspection', id=inspection.id))

        return render_template('inspections/create.html', form=form)

    @app.route('/inspections/<int:id>', methods=['GET'])
    def show_inspection(id):
        inspection = inspections.query.get(id)
        return render_template('inspections/show.html', inspection=inspection, aiot=inspection.aiot)

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

    @app.route('/inspections/<int:inspection_id>/controles/nouveau', methods=['GET', 'POST'])
    def create_controle(inspection_id):
        form = CreateControleInspForm()

        if form.validate_on_submit():
            controle = controles()
            controle.insp_id = inspection_id
            form.populate_obj(controle)
            db.session.add(controle)
            db.session.commit()
            return redirect(url_for('show_inspection', id=inspection_id))
        
        return render_template('controles/create.html', form=form)

    @app.route('/inspections/controles/<int:id>/edit', methods=['GET', 'POST'])
    def edit_controle(id):
        controle = controles.query.get(id)
        form = EditControleInspForm(obj=controle)
        
        if form.validate_on_submit():
            form.populate_obj(controle)
            db.session.add(controle)
            db.session.commit()
            return redirect(url_for('show_inspection', id=controle.insp_id))
        
        return render_template('controles/edit.html', form=form)

    @app.route('/inspections/controles/<int:id>/delete', methods=['GET'])
    def delete_controle(id):
        controle = controles.query.get(id)
        insp_id = controle.insp_id
        db.session.delete(controle)
        db.session.commit()
        return redirect(url_for('show_inspection', id=insp_id))

    @app.route('/demandes_exploitant/nouveau', methods=['GET', 'POST'])
    def create_demande_exploitant():
        form = CreateDemandeExploitant()

        if form.validate_on_submit():
            demande_exploitant = demandes_exploitant()
            form.populate_obj(demande_exploitant)
            db.session.add(demande_exploitant)
            db.session.flush()
            db.session.refresh(demande_exploitant)
            
            if request.args.get('controle_id'):
                controle_id = request.args.get('controle_id')
                db.session.add(
                    controles_demandes_exploitant_rels(
                        controle_id,
                        demande_exploitant.id
                    )
                )

            db.session.commit()
            
            next = request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            if not is_safe_url(next):
                return abort(400)

        return render_template("create_demande_exploitant.html", form=form)
    
    @app.route('/demandes_exploitant/<int:id>/delete', methods=['GET'])
    def delete_demande_exploitant(id):
        demande = demandes_exploitant.query.get(id)
        db.session.delete(demande)
        db.session.commit()

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index'))

    @app.route('/demandes/avis_pc', methods=['GET', 'POST'])
    def demande_avis_pc():
        from . import docgen
        form = ReponseAvisPCForm()

        if form.validate():
            args = {}
            for field in form:
                args[field.name] = field.data

            stream = docgen.generate_reponse_avis_pc(**args)
            file_name = "Avis_PC_{}.odt".format(args['reference_pc'])
            return send_file(stream, download_name=file_name, mimetype='application/vnd.oasis.opendocument.text')

        return render_template("avis_pc/form.html", form=form)

    @app.route('/arretes/<int:id>', methods=['GET', 'POST'])
    def show_arrete(id):
        arrete = arretes.query.get(id)
        return render_template("arretes/show.html", arrete=arrete)        

    @app.route('/arretes/<int:id>/generate', methods=['GET'])
    def generate_arrete(id):
        from . import docgen
        from datetime import date

        arrete = arretes.query.get(id)
        stream = docgen.generate_arrete(arrete)

        file_name = "{}_{}_{}_{}.odt".format(
            date.today().strftime("%Y%m%d"),
            arrete.aiot.commune,
            arrete.aiot.nom,
            "Arrete"
        )

        return send_file(stream, download_name=file_name, mimetype='application/vnd.oasis.opendocument.text')

    @app.route('/aiots/<int:aiot_id>/arretes/nouveau', methods=['GET', 'POST'])
    def create_arrete(aiot_id):
        form = CreateArreteForm()
        
        form.aiot_id.choices = list(map(lambda aiot: (aiot.id, aiot.nom), aiots.query.all()))
        form.aiot_id.data = aiot_id

        if form.validate_on_submit():
            arrete = arretes()
            form.populate_obj(arrete)
            db.session.add(arrete)
            db.session.flush()
            db.session.refresh(arrete)

            if request.args.get('inspection_id'):
                inspection_id = request.args.get('inspection_id')
                db.session.add(arretes_inspections_rels(arrete.id, inspection_id))

            db.session.commit()

            next = request.args.get('next')

            if not is_safe_url(next):
                return abort(400)

            return redirect(next or url_for('show_arrete', arrete.id))

        return render_template("arretes/create.html", form=form)

    @app.route('/arretes/<int:id>/edit', methods=['GET', 'POST'])
    def edit_arrete(id):
        arrete = arretes.query.get(id)
        form = EditArreteForm(obj=arrete)
        
        form.aiot_id.choices = list(map(lambda aiot: (aiot.id, aiot.nom), aiots.query.all()))
        form.aiot_id.data = arrete.aiot_id
        
        if form.validate_on_submit():
            form.populate_obj(arrete)
            db.session.add(arrete)
            db.session.commit()
            return redirect(url_for('show_arrete', id=arrete.id))
        
        return render_template('arretes/edit.html', form=form)
    


    @app.route('/arretes/<int:arrete_id>/articles/nouveau', methods=['GET', 'POST'])
    def create_article(arrete_id):
        form = CreateArticleForm()
        
        if form.validate_on_submit():
            article = articles()
            article.arrete_id = arrete_id
            form.populate_obj(article)
            db.session.add(article)
            db.session.commit()

            return redirect(url_for('show_arrete', id=arrete_id))

        return render_template("articles/create.html", form=form)

    @app.route('/articles/<int:id>/edit', methods=['GET', 'POST'])
    def edit_article(id):
        article = articles.query.get(id)
        form = EditArticleForm(obj=article)
        
        if form.validate_on_submit():
            form.populate_obj(article)
            db.session.add(article)
            db.session.commit()
            return redirect(url_for('show_arrete', id=article.arrete_id))
        
        return render_template('articles/edit.html', form=form)

    @app.route('/articles/<int:article_id>/dispositions/abrogatoires/nouveau', methods=['GET', 'POST'])
    def create_disposition_abrogatoire(article_id):
        form = CreateDispositionAbrogatoireForm()
        article = articles.query.get(article_id)

        if form.validate_on_submit():
            disposition = dispositions_abrogatoires()
            disposition.article_id = article.id
            form.populate_obj(disposition)
            db.session.add(disposition)
            db.session.commit()

            return redirect(url_for('show_arrete', id=article.arrete_id))

        return render_template("dispositions_abrogatoires/create.html", form=form)

    @app.route('/dispositions/abrogatoires/<int:id>/edit', methods=['GET', 'POST'])
    def edit_disposition_abrogatoire(id):
        disposition = dispositions_abrogatoires.query.get(id)
        article = articles.query.get(disposition.article_id)

        form = EditDispositionAbrogatoireForm(obj=disposition)
        
        if form.validate_on_submit():
            form.populate_obj(disposition)
            db.session.add(disposition)
            db.session.commit()
            return redirect(url_for('show_arrete', id=article.arrete_id))
        
        return render_template('dispositions_abrogatoires/edit.html', form=form)

    @app.route('/articles/<int:article_id>/dispositions/autres/nouveau', methods=['GET', 'POST'])
    def create_disposition_autre(article_id):
        form = CreateDispositionAutreForm()
        article = articles.query.get(article_id)

        if form.validate_on_submit():
            disposition = dispositions_autres()
            disposition.article_id = article.id
            form.populate_obj(disposition)
            db.session.add(disposition)
            db.session.commit()

            return redirect(url_for('show_arrete', id=article.arrete_id))

        return render_template("dispositions_autres/create.html", form=form)

    @app.route('/dispositions/autres/<int:id>/edit', methods=['GET', 'POST'])
    def edit_disposition_autre(id):
        disposition = dispositions_autres.query.get(id)
        article = articles.query.get(disposition.article_id)

        form = EditDispositionAutreForm(obj=disposition)
        
        if form.validate_on_submit():
            form.populate_obj(disposition)
            db.session.add(disposition)
            db.session.commit()
            return redirect(url_for('show_arrete', id=article.arrete_id))
        
        return render_template('dispositions_autres/edit.html', form=form)