from geraldo.generators.base import ReportGenerator
from geraldo.widgets import ObjectValue


class TemplateGenerator(ReportGenerator):
    """This is a generator to output a XHTML that uses a Django template.

    The generator simply passes the report object to the template and renders
    it saving it to self.filename.
    The template is responsible for all the actual rendering logic.
    """

    filename = None

    def __init__(self, report, filename, template,
                 first_row_with_column_names=False, extra_context=None):
        super(TemplateGenerator, self).__init__(report, filename)
        self.filename = filename
        self.template = template
        self.first_row_with_column_names = first_row_with_column_names
        self.extra_context = extra_context

    def execute(self):
        super(TemplateGenerator, self).execute()

        try:
            from django.template import Context
            from django.template.loader import render_to_string
        except ImportError:
            raise ValueError('TemplateGenerator only works with Django.')

        # Makes a sorted list of columns
        columns = [el for el in self.report.band_detail.elements if isinstance(el, ObjectValue)]
        columns.sort(lambda a,b: cmp(a.left, b.left) or cmp(a.width, b.width))

        # Makes a 2D list of the widgets.
        objects = self.report.get_objects_list()
        report_widgets = []
        for obj in objects:
            row = []
            for element in columns:
                widget = element.clone()
                # Set widget basic attributes
                widget.instance = obj
                widget.generator = self
                widget.report = self.report
                widget.band = self.report.band_detail
                widget.page = None
                widget.css_classes = getattr(element, 'css_classes', [])
                # Sets the style attribute.
                widget.style = element.style
                row.append(widget)
            report_widgets.append(row)

        # Band summary.
        if self.report.band_summary:
            report_band_summary = []
            for element in self.report.band_summary.elements:
                widget = element.clone()
                widget.generator = self
                widget.report = self.report
                widget.band = self.report.band_summary
                widget.page = None
                widget.css_classes = getattr(element, 'css_classes', [])
                widget.style = element.style
                report_band_summary.append(widget)

        self.report.do_before_print(generator=self)
        context = Context({
            'report': self.report,
            'report_band_summary': report_band_summary,
            'report_columns': columns,
            'report_first_row_with_column_names': self.first_row_with_column_names,
            'report_objects': objects,
            'report_widgets': report_widgets
        })
        if self.extra_context:
            context.update(self.extra_context)
        self.filename.write(render_to_string(self.template, context))

        self.report.do_after_print(generator=self)
