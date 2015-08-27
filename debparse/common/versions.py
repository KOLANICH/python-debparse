# coding: utf-8

from __future__ import unicode_literals

import functools
import itertools
import string


@functools.total_ordering
class Version(object):

    def __init__(self, upstream, epoch=None, revision=None):
        self.upstream = upstream
        self.epoch = epoch
        self.revision = revision

    @classmethod
    def from_string(cls, version):
        if ':' in version:
            epoch, version = version.split(':', 1)
        else:
            epoch = None

        if '-' in version:
            version, revision = version.rsplit('-', 1)
        else:
            revision = None

        return cls(
            epoch=epoch,
            upstream=version,
            revision=revision
        )

    def __hash__(self):
        return hash(self.upstream) ^ hash(self.epoch) ^ hash(self.revision)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented
        return all([
            self.epoch == other.epoch,
            self.upstream == other.upstream,
            self.revision == other.revision,
        ])

    def __gt__(self, other):
        if self.epoch != other.epoch:
            self_epoch = self.epoch or 0
            other_epoch = other.epoch or 0
            return self_epoch > other_epoch

        if self.upstream != other.upstream:
            return is_debian_version_gt(self.upstream, other.upstream)

        if self.revision != other.revision:
            self_revision = self.revision or ''
            other_revision = other.revision or ''
            return is_debian_version_gt(self_revision, other_revision)

        return False

    def __str__(self):
        formatted = ''
        if self.epoch:
            formatted += self.epoch + ':'
        formatted += self.upstream
        if self.revision:
            formatted += '-' + self.revision
        return formatted

    def __repr__(self):
        return '<Version %s>' % self

    __unicode__ = __str__


def is_debian_version_gt(ver_one, ver_two):
    """
    Compare debian version strings as described in
    https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Version

    validate with
    dpkg --compare-versions 1.1 gt 1.2 && echo 'greater' || echo 'lesser or eq'
    """
    ver_one_pieces = split_string_alpha_digit(ver_one)
    ver_two_pieces = split_string_alpha_digit(ver_two)

    zipped = itertools.izip_longest(
        ver_one_pieces, ver_two_pieces, fillvalue='')

    is_comparing_alpha = True
    for piece_one, piece_two in zipped:
        if piece_one != piece_two:
            if is_comparing_alpha:
                return is_string_lexically_gt(piece_one, piece_two)
            else:
                return is_digit_string_gt(piece_one, piece_two)

        is_comparing_alpha = not is_comparing_alpha

    return False


def split_string_alpha_digit(version_string):
    """
    Split version in non-digit and digit intervals.
    https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Version
    """
    pieces = []
    current_type = 'alpha'
    current_interval = ''

    for symbol in version_string:
        if current_type == 'alpha' and symbol.isdigit():
            pieces.append(current_interval)
            current_type, current_interval = 'digit', symbol
        elif current_type == 'digit' and not symbol.isdigit():
            pieces.append(current_interval)
            current_type, current_interval = 'alpha', symbol
        else:
            current_interval += symbol
    pieces.append(current_interval)

    return pieces


def is_string_lexically_gt(str_one, str_two):
    zipped = itertools.izip_longest(str_one, str_two, fillvalue='')
    for symbol_one, symbol_two in zipped:
        if symbol_one != symbol_two:
            return is_symbol_lexically_gt(symbol_one, symbol_two)
    return False


def is_symbol_lexically_gt(symbol_one, symbol_two):
    ordered_symbols = string.ascii_letters + '+-.:'

    def get_priority(symbol):
        if symbol == '':
            return -1
        if symbol == '~':
            return -2
        return ordered_symbols.index(symbol)
    return get_priority(symbol_one) > get_priority(symbol_two)


def is_digit_string_gt(str_one, str_two):
    def to_int(int_string):
        if int_string == '':
            return 0
        return int(int_string)

    return to_int(str_one) > to_int(str_two)
