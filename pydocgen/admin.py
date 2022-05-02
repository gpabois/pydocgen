from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .models import db, demandes_exploitant, insp_controles_demandes_exploitant

admin = Admin(template_mode='bootstrap3')
admin.add_view(ModelView(demandes_exploitant, db.session))
admin.add_view(ModelView(insp_controles_demandes_exploitant, db.session))
