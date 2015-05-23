# coding: utf-8

from .import deb_control
from . import utils

CONTROL_EXAMPLE = '/Users/l0ki/dev/python/libs/debparse/files/debian_control_example'
control_file_data = deb_control.parse(path=CONTROL_EXAMPLE)
print control_file_data.packages
