# coding: utf-8

import pytest

from debparse.deb_control import fields, classes

from . import examples


def test_get_raw_key_value_simple():
    parsed = fields.get_raw_key_value(examples.SIMPLE_FIELD)
    assert parsed == ('Source', 'nginx')


def test_get_raw_key_value_multiline():
    parsed = fields.get_raw_key_value(examples.MULTILINE_FIELD)
    key, value = parsed
    assert key == 'Build-Depends'
    assert ',' in value
    assert '\n' in value
    assert 'autotools-dev' in value
    assert 'dpkg-dev (>= 1.15.7)' in value
    assert 'zlib1g-dev' in value


def test_parse_field_value_single_value():
    meta = classes.FieldMeta(format='single', type='simple')
    parsed = fields.parse_field_value("WAT", meta)
    assert parsed.text == "WAT"


def test_parse_field_value_comma_separated_list():
    FIELD_VALUE = """one, two,
        three,
        four,
    """.strip()
    meta = classes.FieldMeta(format='list', type='simple')
    parsed = fields.parse_field_value(FIELD_VALUE, meta=meta)

    assert [val.text for val in parsed] == [
        'one',
        'two',
        'three',
        'four',
    ]


def test_parse_field_type_contact():
    value = 'Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>'
    parsed = fields.parse_field_type_contact(value)

    name, email = parsed.name, parsed.email
    assert name == 'Ubuntu Developers'
    assert email == 'ubuntu-devel-discuss@lists.ubuntu.com'


@pytest.mark.parametrize('input,expected', [
    (
        'libc6', 'libc6'
    ),
    (
        'libc (= 3)', ('libc', '=', '3')
    ),
    (
        'libc (>= 3)', ('libc', '>=', '3')
    ),
    (
        'libc (<= 3)', ('libc', '<=', '3')
    ),
    (
        'libc (>> 3)', ('libc', '>>', '3')
    ),
    (
        'libc (<< 3)', ('libc', '<<', '3')
    ),
    (
        'libc(=3)', ('libc', '=', '3')
    ),
    (
        'libc (= 1:1.5~+-:alpha-deb3)', ('libc', '=', '1:1.5~+-:alpha-deb3')
    ),
    (
        'libc6+xxx-bla.wat (= 3)', ('libc6+xxx-bla.wat', '=', '3')
    ),
    (
        'kernel-headers-2.2.10 (= 2)', ('kernel-headers-2.2.10', '=', '2')
    ),
    (
        'aa (= 1) | bb (>> 2)', [
            ('aa', '=', '1'),
            ('bb', '>>', '2'),
        ]
    ),
    (
        '${misc: Depends}', (None, None, None, '${misc: Depends}')
    ),
    (
        'foo [!i386]', ('foo', None, None, None, '!i386')
    ),
])
def test_parse_field_type_dependency(input, expected):
    meta = classes.FieldMeta(type='dependency')
    parsed = fields.parse_typed_field_value(input, meta)

    def assert_expectations(parsed, expected):
        assert parsed is not None
        if isinstance(expected, tuple) and len(expected) == 5:
            name, relation, version, placeholder, architecture = expected
        elif isinstance(expected, tuple) and len(expected) == 4:
            name, relation, version, placeholder = expected
            architecture = None
        elif isinstance(expected, tuple) and len(expected) == 3:
            name, relation, version = expected
            placeholder = architecture = None
        else:
            name = expected
            relation = version = placeholder = architecture = None

        if placeholder:
            assert parsed.name == placeholder
        else:
            assert parsed.name == name

        parsed_relation = parsed.restriction and parsed.restriction.relation
        assert parsed_relation == relation

        parsed_version = parsed.restriction and parsed.restriction.version
        assert parsed_version == version
        assert parsed.architecture == architecture

    if isinstance(expected, list):
        assert isinstance(parsed, classes.DependencyAlternative)
        assert len(parsed.alternatives) == len(expected)
        for parsed_val, expected_val in zip(parsed.alternatives, expected):
            assert_expectations(parsed_val, expected_val)
    else:
        assert_expectations(parsed, expected)
