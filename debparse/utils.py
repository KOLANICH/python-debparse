# coding: utf-8
from __future__ import unicode_literals

import codecs

from functools import partial


def get_file_contents(path):
    with codecs.open(path, "r", "utf-8") as f:
        return f.read()


def split_string(string, separator, strip=False, skip_blank=False):
    result = []

    for piece in string.split(separator):
        if strip:
            piece = piece.strip()
        if skip_blank and not piece:
            continue
        result.append(piece)

    return result


def join_string_list(string_list, joiner):
    return joiner.join(string_list)


split_string_by_newline = partial(split_string, separator='\n')
split_string_by_comma = partial(split_string, separator=',')
split_string_by_bar = partial(split_string, separator='|')
join_string_list_with_newline = partial(join_string_list, joiner='\n')
join_string_list_with_space = partial(join_string_list, joiner=' ')
