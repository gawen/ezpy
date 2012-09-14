"""
An unpretentious set of helpers to log.

>>> import log
>>> log.init()

This module uses the config module to set the default level verbosity and set
specific level for the loggers you want. For example, if the configuration
file contains:

1 [log]
2 default=INFO
3 server.listener=DEBUG
4 mail.sender=CRITICAL

This will set the default level as INFO. The logger 'server.listener' will be
set to DEBUG, while 'mail.sender' will only prints when a critical log is sent.

>>> logger = log.getLogger("foo")
>>> logger.info("Hello, World! :-)")
INFO:foo:Hello, World! :-)

It is sometimes useful to log before and after an specific operation, animpod
potentially when an exception is raised during the process. A useful method
is added in this module to do this job.

>>> with logger.context(log.INFO, "Print some nice words"):
...     print "Hello, World! :-)"
DEBUG:foo:Printing some nice words.
Hello, World! :-)
INFO:foo:Some nice words printed.

If something bad happens

>>> with logger.info_context("Print some nice words"):
...     ThisWillFail
DEBUG:foo:Printing some nice words.
ERROR:foo:Cannot print some nice words.
Traceback (most recent call last):
  File "test.py", line 9, in <module>
    ThisWillFail
NameError: name 'ThisWillFail' is not defined

You can also decorate a function to make it contextually logged.

>>> @logger.info_context("Sum two numbers")
... def sum(a, b):
...     return a + b
>>> sum(2, 2)
DEBUG:foo:Suming two numbers.
INFO:foo:Two numbers sumed.
4

"""

__author__ = "Gawen"
__license__ = "Beerware"
__version__ = "1.0.0"
__email__ = "g@wenarab.com"
__status__ = "Production"

from logging import *
import contextlib
import functools
import config

LEVELS = (DEBUG, INFO, WARNING, ERROR, CRITICAL, )
LEVEL_NAMES = {
    CRITICAL : 'CRITICAL',
    ERROR : 'ERROR',
    WARNING : 'WARNING',
    INFO : 'INFO',
    DEBUG : 'DEBUG',
    NOTSET : 'NOTSET',
    'CRITICAL' : CRITICAL,
    'ERROR' : ERROR,
    'WARN' : WARNING,
    'WARNING' : WARNING,
    'INFO' : INFO,
    'DEBUG' : DEBUG,
    'NOTSET' : NOTSET,
}

class context(object):
    def __init__(self, logger, message, level = None):
        level = level if level is not None else INFO
        assert len(message)
        
        super(context, self).__init__()

        message = message.split(" ", 1)
        verb = message[0].lower()
        if len(message) > 1:
            message = message[1]
        else:
            message = ""

        verb_ = verb + "-" if verb.endswith("e") else verb

        self.logger = logger
        self.message = message
        self.level = level
        self.verb = verb
        self.verb_ = verb_

    def __enter__(self):
        self.logger.debug(self.verb_.capitalize() + "ing " + self.message + ".")

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None:
            self.logger.log(self.level, self.message.capitalize() + " " + self.verb_ + "ed.")
        
        else:
            self.logger.error("Cannot " + self.verb + " " + self.message + ".")

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*kargs, **kwargs):
            with self:
                return func(*kargs, **kwargs)
        return wrapper

def _patch_logger_context():
    def method_context(self, *kargs, **kwargs):
        return context(self, *kargs, **kwargs)
    Logger.context = method_context
    
    level_strs = ("debug", "info", "warning", "error", "critical", )

    for level_str in level_strs:
        def logger_context_builder(level_str):
            level = LEVEL_NAMES[level_str.upper()]
            def logger_context(self, message):
                return self.context(message, level)
            return logger_context

        setattr(Logger, "%s_context" % (level_str, ), logger_context_builder(level_str))

_patch_logger_context()

def init(level = None):
    LEVELS = {
        "debug": DEBUG, 
        "info": INFO, 
        "warning": WARNING,
        "critical": CRITICAL,
    }
    
    level = level if level is not None else LEVELS[config.get("log", "default", "INFO").lower()]
    
    basicConfig()
    getLogger().setLevel(level)

    # Set level loggers
    for logger in config.options("log"):
        if logger == "default":
            continue

        logger_level = config.get("log", logger, level)

        getLogger(logger).setLevel(LEVELS[logger_level.lower()])

