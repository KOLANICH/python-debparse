# coding: utf-8
from __future__ import unicode_literals

CONTROL_FILE_DATA = """
Source: nginx
Section: httpd
Priority: optional
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
XSBC-Original-Maintainer: Kartik Mistry <kartik@debian.org>
Uploaders: Jose Parrella <bureado@debian.org>,
           Fabio Tranchitella <kobold@debian.org>,
           Cyril Lavier <cyril.lavier@davromaniak.eu>
Build-Depends: autotools-dev,
               debhelper (>= 7),
               dpkg-dev (>= 1.15.7),
               libxslt1-dev,
               zlib1g-dev
Standards-Version: 3.9.3
Homepage: http://nginx.net

Package: nginx
Architecture: all
Depends: nginx-full | nginx-light, ${misc:Depends}
Description: small, but very powerful and efficient web server and mail proxy
 Nginx (engine x) is a web server created by Igor Sysoev.
 .
 This is a dummy package that selects nginx-full by default.

Package: nginx-doc
Architecture: all
Section: doc
Depends: lsb-base (>= 3.2-14), ${misc:Depends}
Description: small, but very powerful and efficient web server (documentation)
 Nginx (engine x).
 .
 This package provides extra documentation to help unleash the power of Nginx.

"""

PARAGRAPH = """
Source: nginx
Uploaders: Jose Parrella <bureado@debian.org>,
           Cyril Lavier <cyril.lavier@davromaniak.eu>
Build-Depends: autotools-dev,
               dpkg-dev (>= 1.15.7),
               zlib1g-dev
Standards-Version: 3.9.3
""".strip()


SIMPLE_FIELD = "Source: nginx"
MULTILINE_FIELD = """
Build-Depends: autotools-dev,
               dpkg-dev (>= 1.15.7),
               zlib1g-dev
"""
