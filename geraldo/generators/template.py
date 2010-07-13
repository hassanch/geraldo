from geraldo.generators.base import ReportGenerator


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
            from django.template.loader import render_to_string
        except ImportError:
            raise ValueError('TemplateGenerator only works with Django.')

        self.report.do_before_print(generator=self)
        context = {
            'report': self.report,
            'objects': self.report.get_objects_list()
        }
        if self.extra_context:
            context.update(self.extra_context)
        self.filename.write(render_to_string(self.template, context))

        self.report.do_after_print(generator=self)
