# coding: utf-8

from __future__ import unicode_literals

import random

import pytest

from debparse import versions


@pytest.mark.parametrize("version,splitted", [
    ('a', ['a']),
    ('a1', ['a', '1']),
    ('1a', ['', '1', 'a']),
    ('1a1', ['', '1', 'a', '1']),
    ('a1a', ['a', '1', 'a']),
    ('aa', ['aa']),
    ('aa11', ['aa', '11']),
    ('aa11aa', ['aa', '11', 'aa']),
    ('aa11aa11', ['aa', '11', 'aa', '11']),
    ('a1.1a', ['a', '1', '.', '1', 'a']),
    ('1.1', ['', '1', '.', '1']),
    ('1~a', ['', '1', '~a']),
    ('1~1', ['', '1', '~', '1']),
])
def test_split_version(version, splitted):
    assert versions.split_string_alpha_digit(version) == splitted


@pytest.mark.parametrize("ordered_strings", [
    ('a', '', '~', '~~a', '~~'),
    ('a:', 'a.', 'a-', 'a+', 'a', 'a~'),
])
def test_is_string_lexically_gt(ordered_strings):
    for index, str_one in enumerate(ordered_strings):
        for str_two in ordered_strings[index + 1:]:
            fail_msg = '`%s` expected to be greater than `%s`' % (
                str_one, str_two)
            assert versions.is_string_lexically_gt(str_one, str_two), fail_msg


@pytest.mark.parametrize('big,small', [
    ('2', '1'),
    ('123', '11'),
    ('1b', '1a'),
    ('1a2', '1a1'),
    ('1a1', '1a'),
    ('1', '1~svn1'),
    ('1+patches', '1'),
    ('1.3', '1.2'),
    ('1.2-11', '1.2-10'),
    ('1.2.precise.2', '1.2.precise.1'),
    ('1.2.precise.1', '1.2.precise.1~alpha'),
    ('9.20120115ubuntu3', '9.20120115ubuntu2'),
])
def test_is_debian_version_gt(big, small):
    fail_msg = '`%s` expected to be greater than `%s`' % (big, small)
    assert versions.is_debian_version_gt(big, small), fail_msg


def test_version_sort():
    ordered = (
        '1:1.0-ubuntu1',
        '1:1.0',
        '1.2-ubuntu1',
        '1.2',
        '1.1',
        '1alpha',
        '1alpha~svn666-ubuntu1',
        '1alpha~svn666',
        '1',
        '1~svn666',
    )
    ordered = map(versions.Version.from_string, ordered)
    shuffled = ordered[:]
    random.shuffle(shuffled, lambda: 0)  # predictable shuffle for tests

    assert sorted(shuffled, reverse=True) == ordered
