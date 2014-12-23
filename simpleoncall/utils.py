import os.path

from simpleoncall import settings


def print_stylesheets():
    for output_filename, input_files in settings.STYLESHEETS.iteritems():
        output_filename = os.path.join(settings.STATIC_ROOT, output_filename)
        input_files = ' '.join(os.path.join(settings.STATIC_ROOT, i) for i in input_files)
        print '%s %s' % (output_filename, input_files)
