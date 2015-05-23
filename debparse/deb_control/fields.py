# coding: utf-8
from __future__ import unicode_literals

import re
import logging

from debparse import utils
from . import classes


log = logging.getLogger(__name__)


FIELDS = {
    'Architecture': 'enum',
    'Breaks': 'list/dependency',
    'Build-Depends': 'list/dependency',
    'Conflicts': 'list/dependency',
    'Depends': 'list/dependency',
    'Description': 'text',
    'Homepage': 'uri',
    'Maintainer': 'contact',
    'Package': 'simple',
    'Priority': 'optional',
    'Provides': 'list/dependency',
    'Replaces': 'list/dependency',
    'Section': 'enum',
    'Source': 'simple',
    'Standards-Version': 'version',
    'Uploaders': 'list/contact',
}


def parse_field(data):
    """
    `data` should be field-like string, kind of
    'Homepage: http://example.com'
    or
    'Depends: libc, bash, \n debhelper (>= 9)'

    The field name is composed of US-ASCII characters excluding
    control characters, space, and colon (i.e., characters in the ranges
    33-57 and 59-126, inclusive). Field names must not begin with the
    comment character, #, nor with the hyphen character, -.
    """
    key, value = get_raw_key_value(data)
    field_meta = get_field_meta(key)
    parsed_value = parse_field_value(value, meta=field_meta)
    return key, parsed_value


def get_raw_key_value(data):
    key, value = data.split(':', 1)
    key = key.strip()
    value = value.strip()
    return key, value


def lookup_field_spec(key):
    for canonical_name, spec in FIELDS.items():
        if key.lower() == canonical_name.lower():
            return canonical_name, spec
    return 'Unknown', 'single/simple'


def get_field_meta(key):
    canonical_name, spec = lookup_field_spec(key)
    if '/' in spec:
        format, type = spec.split('/')
    else:
        format, type = 'single', spec

    return classes.FieldMeta(
        format=format,
        type=type,
        canonical_name=canonical_name,
    )


def parse_field_value(raw_value, meta=None):
    if meta and meta.format == 'list':
        if ',' in raw_value:
            separator = ','
        else:
            separator = '\n'
        list_items = utils.split_string(
            raw_value, separator=separator, strip=True, skip_blank=True)
        return [parse_typed_field_value(li, meta) for li in list_items]
    else:
        return parse_typed_field_value(raw_value, meta)


def parse_typed_field_value(raw_value, meta=None):
    type_parser_name = 'parse_field_type_' + meta.type
    type_parser = globals().get(type_parser_name, parse_field_type_simple)
    return type_parser(raw_value, meta)


def parse_field_type_simple(raw_value, meta=None):
    return classes.SimpleField(
        _raw=raw_value,
        meta=meta,
        text=raw_value
    )


def parse_field_type_contact(raw_value, meta=None):
    name, email = raw_value.rsplit(' ', 1)
    parsed_email = email.strip('<>')
    return classes.ContactField(
        _raw=raw_value,
        meta=meta,
        name=name,
        email=parsed_email,
    )


# https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Source
# https://www.debian.org/doc/debian-policy/ch-relationships.html
# https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Version
# https://www.debian.org/doc/manuals/maint-guide/dreq.en.html#control
DEPENDENCY_PATTERN = re.compile(r"""
    (
        # Package names must consist only of lower case letters (a-z),
        # digits (0-9), plus (+) and minus (-) signs, and periods (.).
        # They must be at least two characters long and must start with an
        # alphanumeric character.
        (?P<name>[a-z0-9][a-z0-9+\-\.]+)
        # Whitespace may appear at any point in the version specification
        # subject to the rules in Syntax of control files
        [ ]*
        # optional version restriction
        (
            \(
                # The relations allowed are <<, <=, =, >= and >> for strictly
                # earlier, earlier or equal, exactly equal, later or equal and
                # strictly later, respectively. The deprecated forms < and >
                # were confusingly used to mean earlier/later or equal, rather
                # than strictly earlier/later, and must not appear in new
                # packages (though dpkg still supports them with a warning).
                (?P<relation>(<<|>>|<=|>=|=))
                # some optional whitespaces
                [ ]*
                # The format is: [epoch:]upstream_version[-debian_revision]
                # For now let's be forgiving about version, because validation
                # is not the case in this library.
                (?P<version>.+)
            \)
        )?
        # optional whitespaces
        [ ]*
        # Relationships may be restricted to a certain set of
        # architectures. This is indicated in brackets after each
        # individual package name and the optional version specification.
        # The brackets enclose a non-empty list of Debian architecture
        # names in the format described in Architecture specification
        # strings, separated by whitespace.
        (
            \[(?P<architecture>.+)\]
        )?
    # OR
    |
        # dh_gencontrol(1) generates DEBIAN/control for each binary package
        # while substituting
        # ${shlibs:Depends}, ${perl:Depends}, ${misc:Depends}, etc.
        (?P<placeholder>\$\{.+\})
    )
""", re.VERBOSE)


def parse_field_type_dependency(raw_value, meta=None):
    if '|' in raw_value:
        raw_value = utils.split_string(raw_value, separator='|', strip=True)
        alternatives = []
        for dependency in raw_value:
            match = re.match(DEPENDENCY_PATTERN, dependency)
            if match:
                parsed = match.groupdict()
                alternatives.append(_build_dependency_class(
                    parsed=parsed,
                    raw_value=raw_value,
                    meta=meta
                ))
            else:
                log.warning('Dependency parse error on %s', dependency)
                # TODO: add some UnparsedVersion object
        return classes.DependencyAlternative(
            _raw=raw_value,
            alternatives=alternatives
        )
    else:
        match = re.match(DEPENDENCY_PATTERN, raw_value)
        if match is None:
            return
        else:
            parsed = match.groupdict()
            return _build_dependency_class(
                parsed=parsed,
                raw_value=raw_value,
                meta=meta,
            )


def _build_dependency_class(parsed, raw_value, meta):
    name = parsed['name']

    relation = parsed['relation']
    version = parsed['version']
    architecture = parsed['architecture']
    placeholder = parsed['placeholder']

    if placeholder:
        return classes.DependencyPlaceholder(
            _raw=raw_value,
            meta=meta,
            name=placeholder,
            restriction=None,
            architecture=None,
        )
    else:
        return classes.DependencySimple(
            _raw=raw_value,
            meta=meta,
            name=name,
            restriction=classes.Restriction(
                relation=relation,
                version=version,
            ) if version else None,
            architecture=architecture,
        )
