import io
import os

from secretary import Renderer, UndefinedSilently, pad_string
from flask import current_app

from jinja2 import Environment
from markupsafe import Markup

def finalize_value(value):
    if isinstance(value, Markup):
            return value

    # get_escaped_var_value is a static method.
    return Markup(Renderer.get_escaped_var_value(value))

def odt_engine():
    environment = Environment(undefined=UndefinedSilently,
                                            autoescape=True,
                                            finalize=finalize_value)
    
    environment.filters['pad'] = pad_string
    environment.globals['SafeValue'] = Markup
    environment.globals['enumerate'] = enumerate

    engine = Renderer(environment)
    return engine

def generate_inspection_be_exploitant(inspection):
    stream = io.BytesIO()
       
    engine = odt_engine()

    tpl = os.path.join(current_app.instance_path, "modeles", "insp_be_exploitant.odt")
    doc = engine.render(tpl, 
        inspection=inspection, 
        redacteur=inspection.redacteur, 
        signataire=inspection.verificateur, 
        aiot=inspection.aiot
    )

    stream.write(doc)

    stream.seek(0)
    return stream

def generate_inspection_rapport(inspection):
    stream = io.BytesIO()
       
    engine = odt_engine()

    tpl = os.path.join(current_app.instance_path, "modeles", "insp_rapport.odt")
    doc = engine.render(tpl, 
        inspection=inspection, 
        redacteur=inspection.redacteur, 
        verificateur=inspection.verificateur, 
        approbateur=inspection.approbateur,
        aiot=inspection.aiot
    )

    stream.write(doc)

    stream.seek(0)
    return stream