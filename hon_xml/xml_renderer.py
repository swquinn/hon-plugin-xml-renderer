"""
    hon_xml
    ~~~~~

    :license: MIT, see LICENSE for more details.
"""
import hon
import json
import os
import shutil
from hon.parsing import MarkdownParser
from hon.renderers import Renderer
from hon.utils.fileutils import copy_from, filename_matches_pattern
from io import StringIO
from jinja2 import (
    Environment,
    PackageLoader,
    Template,
    select_autoescape
)
from lxml import etree, html



#: The Hon XML Renderer's path
XML_RENDERER_PATH = os.path.abspath(os.path.dirname(__file__))

#: The path to the XML renderer's tempaltes
XML_RENDERER_TEMPLATE_PATH = os.path.join(XML_RENDERER_PATH, 'templates')


def load_xslt(filepath):
    """Load the XSLT file's contents into memory.

    If the path to the XSLT does not point to a file, raise an error.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError('Unable to find the XSLT file: {}.'.format(filepath))

    xslt_contents = None
    with open(filepath, 'r') as f:
        xslt_contents = etree.parse(f)
    return xslt_contents


class XmlRenderer(Renderer):
    # TODO: Should we allow an option to collect sub chapters into a single file?
    # TODO: Allow overriding the XSLT template for the transforms
    _name = 'xml'

    default_config = {
        'enabled': True,
        'debug_xml': True,
        'insert_linebreaks_for_blocks': True,
        'linebreak_character': '\u2029',
        'xslt_template': os.path.join(XML_RENDERER_TEMPLATE_PATH, 'hon.xslt')
    }

    def __init__(self, app, config=None):
        super(XmlRenderer, self).__init__(app, config=config)

        xslt_template_filepath = self.config.get('xslt_template')
        self.xslt_template = load_xslt(xslt_template_filepath)
        self.transform = etree.XSLT(self.xslt_template)
        #self.parser = etree.XMLParser(remove_blank_text=True)
        self.parser = html.HTMLParser(remove_blank_text=True)

    def on_generate_assets(self, book, context):
        pass

    def on_generate_pages(self, book, context):
        """
        """
        def foo(chapter):
            parts = [chapter]
            for child in chapter.children:
                parts.extend(foo(child))
            return parts

        for chapter in self.chapters:
            filename = '{}.xml'.format(chapter.filename)

            #: Get the item's path, relative to the book's root. This allows
            #: us to actually write the transformed items to a structure that
            #: is similar to the source. [SWQ]
            relative_item_path = os.path.relpath(chapter.path, start=book.path)
            relative_item_dir = os.path.dirname(relative_item_path)

            output_path = os.path.join(context.path, relative_item_dir)
            if not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)

            write_to = os.path.join(output_path, filename)

            pdf_template = context.environment.get_template('chapter.xhtml.jinja')
            data = {
                'chapter': {
                    'title': chapter.name,
                },
                'parts': foo(chapter)
            }
            data.update(context.data)
            output = pdf_template.render(data)

            try:
                document_src = StringIO(output)
                document = html.parse(document_src, self.parser)

                params = dict(
                    add_linebreak='true()' if self.config.get('insert_linebreaks_for_blocks') else 'false()',
                    linebreak=etree.XSLT.strparam(self.config.get('linebreak_character', '\u2028'))
                )
                xml = self.transform(document, **params)
                with open(write_to, 'w') as f:
                    f.write(str(xml))
                #: TODO: if we error out before writing the transformed document
                #:       to a file, it looks like we accrue a lot of detritus
                #:       and fill up. We need a better clean up plan...
            except:
                self.app.logger.exception('Failed to write: {}'.format(chapter.filename))
                raise

            if self.config.get('debug_xml', False):
                self.write_debug_xml(chapter, output_path)

    def on_init(self, book, context):
        """

        :param context: The rendering context for the book.
        :type context: hon.renderers.RenderingContext
        """
        context.configure_environment('templates', pkg='hon_xml')
        return context

    def on_render_page(self, page, book, context):
        """

        :type page: hon.structure.chapter.Chapter
        """
        raw_text = str(page.raw_text)
        parser = MarkdownParser()
        markedup_text = parser.parse(raw_text)

        page_template = context.environment.get_template('page.xhtml.jinja')

        if markedup_text is not None:
            intermediate_template = Template(markedup_text)
            content = intermediate_template.render(book={})

            relative_page_path = os.path.relpath(page.path, start=book.path)
            abs_page_path = os.path.join(context.path, relative_page_path)
            page_dir = os.path.dirname(abs_page_path)
            root_path = os.path.relpath(context.path, start=page_dir)

            node = self.chapter_graph.get(page)
            data = {
                'page': {
                    'title': page.name,
                    'content': content,
                    'root_path': root_path,
                    'previous_chapter': node.previous.chapter if node.previous else None,
                    'next_chapter': node.next.chapter if node.next else None,
                }
            }
            data.update(context.data)

            content = page_template.render(data)
            page.text = content

    def write_debug_xml(self, page, path):
        filename = '{}.input'.format(page.filename)
        write_to = os.path.join(path, filename)
        with open(write_to, 'w') as f:
            f.write(page.text)
