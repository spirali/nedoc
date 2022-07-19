from typing import Optional

import markdown


def convert_markdown_to_html(text: Optional[str]) -> str:
    if text is None:
        return ""
    return markdown.markdown(text)
