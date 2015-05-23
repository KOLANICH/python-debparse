# coding: utf-8

from debparse.deb_control import paragraphs

from . import examples


def test_get_raw_paragraphs_correct_count_with_linebreaks():
    data = examples.CONTROL_FILE_DATA
    raw_paragraph = paragraphs.get_raw_paragraphs(data)
    assert len(raw_paragraph) == 3


def test_get_raw_paragraphs_correct_count_stripped_content():
    data = examples.CONTROL_FILE_DATA.strip()
    raw_paragraph = paragraphs.get_raw_paragraphs(data)
    assert len(raw_paragraph) == 3


def test_get_raw_paragraphs_correct_content():
    data = examples.CONTROL_FILE_DATA
    raw_paragraphs = paragraphs.get_raw_paragraphs(data)

    assert raw_paragraphs, 'no paragraphs found, check correct_count tests'
    first_paragraph = raw_paragraphs[0]

    assert first_paragraph.startswith('Source: nginx')
    assert first_paragraph.endswith('Homepage: http://nginx.net')

    last_paragraph = raw_paragraphs[-1]
    assert last_paragraph.startswith('Package: nginx-doc')
    assert last_paragraph.endswith('power of Nginx.')


def test_get_raw_fields_correct_count():
    data = examples.PARAGRAPH
    raw_fields = paragraphs.get_raw_fields(data)
    assert len(raw_fields) == 4


def test_get_raw_fields_correct_content():
    data = examples.PARAGRAPH
    raw_fields = paragraphs.get_raw_fields(data)

    source, uploaders, build_deps, standards = raw_fields
    assert source == 'Source: nginx'
    assert 'Uploaders' in uploaders
    assert '<cyril.lavier@davromaniak.eu>' in uploaders
    assert 'Build-Depends:' in build_deps
    assert 'dpkg-dev (>= 1.15.7),' in build_deps
