# coding: utf-8


from debparse import utils

from . import paragraphs, classes


def parse(path=None, data=None):
    """
    Main deb_control package api method.
    Takes path to debian control file or its contents.
    """
    assert path or data, 'path or data should be given'
    if path:
        data = utils.get_file_contents(path)

    raw_paragraphs = paragraphs.get_raw_paragraphs(data)
    parsed_paragraphs = list(map(paragraphs.parse_paragraph, raw_paragraphs))
    return classes.ControlData(
        _raw=data,
        _path=path,
        packages=parsed_paragraphs,
    )
