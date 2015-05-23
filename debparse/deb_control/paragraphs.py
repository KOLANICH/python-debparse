# coding: utf-8
"""
About debian control file format read
https://www.debian.org/doc/debian-policy/ch-controlfields.html
"""
from __future__ import unicode_literals


from debparse import utils
from . import fields, classes


def get_raw_paragraphs(data):
    """
    A control file consists of one or more paragraphs of fields.
    The paragraphs are separated by empty lines. Parsers may accept
    lines consisting solely of spaces and tabs as paragraph separators,
    but control files should use empty lines.

    :param data: basestring
    :return list of str
    """
    lines = utils.split_string_by_newline(data)

    raw_paragraphs = []
    lines_buffer = []

    for line in lines:
        if line:
            # start or continue form stanza
            lines_buffer.append(line)
        elif not line and lines_buffer:
            # end of paragraph
            raw_paragraphs.append(lines_buffer)
            lines_buffer = []

    # don't forget last paragraph
    if lines_buffer:
        raw_paragraphs.append(lines_buffer)

    return map(utils.join_string_list_with_newline, raw_paragraphs)


def parse_paragraph(data):
    """
    Paragraph `data` must not contain blank lines.
    Each paragraph consists of a series of data fields.
    """
    raw_fields = get_raw_fields(data)
    parsed_fields = map(fields.parse_field, raw_fields)
    return classes.Package(
        parsed_fields,
        _raw=data,
    )


def get_raw_fields(data):
    """
    `data` should be paragraph (str or list of str)
    without blank lines around block, or inside it.
    """
    lines = utils.split_string_by_newline(data)

    blank_symbols = (' ', '\t')

    raw_fields = []
    lines_buffer = []

    for line in lines:
        if not line.startswith(blank_symbols) and lines_buffer:
            # field description beginning and we have something in buffer
            # let's deb_control buffer
            raw_fields.append(lines_buffer)
            # and begin new field handling
            lines_buffer = []

        lines_buffer.append(line)

    # don't forget last line
    if lines_buffer:
        raw_fields.append(lines_buffer)

    return map(utils.join_string_list_with_space, raw_fields)




