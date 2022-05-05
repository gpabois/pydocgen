from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .models import db, demandes_exploitant, controles_demandes_exploitant_rels

admin = Admin(template_mode='bootstrap3')
admin.add_view(ModelView(demandes_exploitant, db.session))
admin.add_view(ModelView(controles_demandes_exploitant_rels, db.session))
