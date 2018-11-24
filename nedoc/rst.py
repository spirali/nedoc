
from docutils.core import publish_parts


def convert_rst_to_html(text, source_filename):
    if text is None:
        return ""
    content = publish_parts(
        text,
        writer_name='html5',
        source_path=source_filename,
        settings_overrides={'initial_header_level': 3})
    return content['html_body']
