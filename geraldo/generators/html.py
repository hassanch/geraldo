from xml.dom.minidom import getDOMImplementation

from geraldo.generators.base import ReportGenerator
from geraldo.widgets import Widget, Label, SystemField, ObjectValue


class HTMLGenerator(ReportGenerator):
    """This is a generator to output a XHTML that uses CSS and best practices
    on standards."""
    filename = None

    def __init__(self, report, filename, first_row_with_column_names=False):
        super(HTMLGenerator, self).__init__(report, filename)
        self.filename = filename
        self.first_row_with_column_names = first_row_with_column_names

    def _get_document(self, attrs=None):
        """Creates and returns a minidom Document.

        The document's doctype is XHTML 1.0 Strict.
        """
        imp = getDOMImplementation()
        dt = imp.createDocumentType(
            'html',
            '-//W3C//DTD XHTML 1.0 Strict//EN',
            'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'
        )
        doc = imp.createDocument('http://www.w3.org/1999/xhtml', 'html', dt)
        # Sets default attributes.
        defaults = {
            'xmlns': 'http://www.w3.org/1999/xhtml',
            'lang': 'en'
        }
        if attrs:
            defaults.update(attrs)
        for key, value in defaults.iteritems():
            doc.documentElement.setAttribute(key, value)
        return doc

    def add_media(self, head):
        """Adds CSS link tags and JS script tags if specified in media."""
        # CSS.
        css = getattr(self.report.media, 'css', {})
        for key, value in css.iteritems():
            for css in value:
                link  = self.document.createElement('link')
                link.setAttribute('media', key)
                link.setAttribute('rel', 'stylesheet')
                link.setAttribute('type', 'text/css')
                link.setAttribute('href', css)
                head.appendChild(link)
        # JS.
        js = getattr(self.report.media, 'js', [])
        for src in js:
            script  = self.document.createElement('script')
            script.setAttribute('type', 'text/javascript')
            script.setAttribute('src', src)
            script.appendChild(self.document.createTextNode(''))
            head.appendChild(script)

    def generate_html(self):
        self.document = self._get_document()
        html = self.document.documentElement

        # Head element.
        head = self.document.createElement('head')
        html.appendChild(head)

        # Media (CSS and JS)
        self.add_media(head)

        # Title element.
        title = self.document.createElement('title')
        title.appendChild(self.document.createTextNode(self.report.title))
        head.appendChild(title)

        # Body element.
        body = self.document.createElement('body')
        html.appendChild(body)

        table = self.document.createElement('table')

        # Make a sorted list of columns
        columns = [el for el in self.report.band_detail.elements if
                   isinstance(el, ObjectValue)]
        columns.sort(lambda a, b: cmp(a.left, b.left) or cmp(a.width, b.width))

        # First row with column names
        if self.first_row_with_column_names:
            thead = self.document.createElement('thead')
            tr = self.document.createElement('tr')
            thead.appendChild(tr)
            for col in columns:
                text = col.name or col.expression or col.attribute_name
                th = self.document.createElement('th')
                th.appendChild(self.document.createTextNode(text))
                tr.appendChild(th)
            table.appendChild(thead)

        # Data rows.
        tbody = self.document.createElement('tbody')
        objects = self.report.get_objects_list()
        for obj in objects:
            tr = self.document.createElement('tr')
            for element in columns:
                td = self.document.createElement('td')
                widget = element.clone()
                # Set widget basic attributes
                widget.instance = obj
                widget.generator = self
                widget.report = self.report
                widget.band = self.report.band_detail
                widget.page = None
                # Sets the style attribute.
                widget.style = element.style
                if widget.style:
                    self.set_style(td, widget.style)
                # Adds the text.
                td.appendChild(self.document.createTextNode(widget.text))
                # Adds the CSS class if specified.
                if hasattr(element, 'class_name'):
                    td.setAttribute('class', element.class_name)
                tr.appendChild(td)
            tbody.appendChild(tr)
        table.appendChild(tbody)

        # Band summary.
        if self.report.band_summary:
            tfoot = self.document.createElement('tfoot')
            tr = self.document.createElement('tr')
            for element in self.report.band_summary.elements:
                td = self.document.createElement('td')
                widget = element.clone()
                widget.generator = self
                widget.report = self.report
                widget.band = self.report.band_summary
                widget.page = None
                widget.style = element.style
                if widget.style:
                    self.set_style(td, widget.style)
                td.appendChild(self.document.createTextNode(widget.text))
                # Adds the CSS class if specified.
                if hasattr(element, 'class_name'):
                    td.setAttribute('class', element.class_name)
                tr.appendChild(td)
            tfoot.appendChild(tr)
            table.appendChild(tfoot)

        body.appendChild(table)

        # Writes pretty xml to writer.
        self.write_xml()

    def write_xml(self):
        """Writes self.document to self.filename."""
        self.document.writexml(self.filename, indent='', addindent='  ',
                               newl='\n', encoding='UTF-8')

    def set_style(self, element, style):
        """Sets an element's CSS style from a dict."""
        style = '; '.join((': '.join((k, v)) for k, v in style.iteritems()))
        if style:
            element.setAttribute('style', style)

    def execute(self):
        super(HTMLGenerator, self).execute()
        self.report.do_before_print(generator=self)
        self.generate_html()
        self.report.do_after_print(generator=self)
