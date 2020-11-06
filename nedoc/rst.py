from docutils.core import publish_parts


def convert_rst_to_html(text):
    if text is None:
        return ""
    content = publish_parts(
        source=text.encode(),
        writer_name='html5',
        settings_overrides={'initial_header_level': 3})
    return content['html_body']
