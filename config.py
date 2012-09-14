"""
An unpretentious helper to access configuration values (read-only).
This takes value from the fact usually a program has only _one_ configuration file
and its handler behaves as a singleton.

>>> import config

Let's say /etc/myprogram.cfg contains

1 [foo]
2 bar=42
3
4 [bar]
5 magic=0xDEADBEAF

>>> config.load("/etc/myprogram.cfg")

Get the value "bar" from section "foo"

>>> config.get("foo", "bar")
"42"

If you try to access a value which doesn't exist

>>> config.get("bar", "foo")
Traceback (most recent call last):
...
ConfigParser.NoOptionError: No option: 'bar'

In such case, you can specify a default value.

>>> config.get("bar", "foo", None)
None

To get all sections

>>> config.sections()
["foo", "bar"]

To get all options from the section "bar"
>>> config.options("bar")
["magic"]

"""

__author__ = "Gawen"
__license__ = "Beerware"
__version__ = "1.0.0"
__email__ = "g@wenarab.com"
__status__ = "Production"

import ConfigParser

class _Config(object):
    class Default:
        pass

    _instance = None

    def __new__(cls):
        if not cls._instance:
            self = super(_Config, cls).__new__(cls)

            self.config = ConfigParser.SafeConfigParser()

            cls._instance = self

        return cls._instance
    
    def load(self, *config_fn):
        self.config.read(config_fn)

    def get(self, section, variable, default = Default):
        try:
            return self.config.get(section, variable)

        except ConfigParser.NoSectionError:
            if default is self.Default:
                raise
            else:
                return default

        except ConfigParser.NoOptionError:
            if default is self.Default:
                raise

            else:
                return default
    
    def options(self, section):
        return self.config.options(section) if self.config.has_section(section) else []

    def sections(self):
        return self.config.sectons()

load = _Config().load
get = _Config().get
options = _Config().options
sections = _Config().sections
