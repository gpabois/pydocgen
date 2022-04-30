import io
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties
from odf.text import H, P, Span
from odf.table import Table, TableRow, TableCell, TableColumn

def _generate_first_page_header(doc: OpenDocumentText):
    doc.text.addElement(
        table(
            tcol(
                trow(
                    tcell(
                        p(text="Logo")
                    )
                )                
            ),
            tcol(
                trow(
                    tcell(
                        p(text="Organisation")
                    )
                )
            )
        )
    )

def _add(node, children):
    for child in children:
        node.addElement(child)

def p(*children, **kwargs):
    p = P(**kwargs)
    _add(p, children)
    return p

def h(*children, **kwargs):
    h = H(**kwargs)
    _add(h, children)
    return h

def span(*children, **kwargs):
    span = Span(**kwargs)
    _add(span, children)
    return span

def tcol(*children):
    tcol = TableColumn()
    _add(tcol, children)
    return tcol

def tcell(*children):
    tcell = TableCell()
    _add(tcell, children)
    return tcell

def trow(*children):
    trow = TableRow()
    _add(trow, children)
    return trow

def table(*children):
    table = Table()
    _add(table, children)
    return table


def generate_rapport_inspection(inspection):
    stream = io.BytesIO()
    doc = OpenDocumentText()

    _generate_first_page_header(doc)

    doc.write(stream)
    stream.seek(0)
    return stream
