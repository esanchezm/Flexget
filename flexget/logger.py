import logging
import logging.handlers
import re


class FlexGetLogger(logging.Logger):
    """Custom logger that adds feed and execution info to log records."""
    execution = ''
    feed = ''

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        extra = {'feed': FlexGetLogger.feed,
                 'execution': FlexGetLogger.execution}
        return logging.Logger.makeRecord(self, name, level, fn, lno, msg, args, exc_info, func, extra)


def set_execution(execution):
    FlexGetLogger.execution = execution


def set_feed(feed):
    FlexGetLogger.feed = feed


class PrivacyFilter(logging.Filter):
    """Edits log messages and <hides> obviously private information."""

    def __init__(self):
        self.replaces = []

        def hide(name):
            s = '([?&]%s=)\w+' % name
            p = re.compile(s)
            self.replaces.append(p)

        for param in ['passwd', 'password', 'pw', 'pass', 'passkey', \
            'key', 'apikey', 'user', 'username', 'uname', 'login', 'id']:
            hide(param)

    def filter(self, record):
        if not isinstance(record.msg, basestring):
            return False
        for p in self.replaces:
            record.msg = p.sub(r'\g<1><hidden>', record.msg)
            record.msg = record.msg
        return False

_logging_configured = False
_mem_handler = None
_logging_started = False


def initialize(unit_test=False):
    global _logging_configured, _mem_handler

    if not _logging_configured:
        logging.addLevelName(5, 'DEBUGALL')
        _logging_configured = True

        if unit_test:
            logging.basicConfig()
            return

        # root logger
        logger = logging.getLogger()

        # time format is same format of strftime
        log_format = ['%(asctime)-15s %(levelname)-8s %(name)-13s %(feed)-15s %(message)s', '%Y-%m-%d %H:%M']
        formatter = logging.Formatter(*log_format)

        _mem_handler = logging.handlers.MemoryHandler(1000 * 1000, 100)
        _mem_handler.setFormatter(formatter)
        logger.addHandler(_mem_handler)
        # hackish way to turn on debug level before optik processes options
        import sys
        if '--debug' in sys.argv:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)


def start(filename=None, level=logging.INFO, debug=False, quiet=False):
    global _logging_configured, _mem_handler, _logging_started

    if not _logging_started:
        if debug:
            hdlr = logging.StreamHandler()
        else:
            hdlr = logging.handlers.RotatingFileHandler(filename, maxBytes=1000 * 1024, backupCount=9)

        hdlr.setFormatter(_mem_handler.formatter)

        _mem_handler.setTarget(hdlr)

        # root logger
        logger = logging.getLogger()
        logger.removeHandler(_mem_handler)
        logger.addHandler(hdlr)
        logger.addFilter(PrivacyFilter())
        logger.setLevel(level)
        logger.getEffectiveLevel()

        if not debug and not quiet:
            console = logging.StreamHandler()
            console.setFormatter(hdlr.formatter)
            logger.addHandler(console)

            # flush memory handler to the console without
            # destroying the buffer
            if len(_mem_handler.buffer) > 0:
                for record in _mem_handler.buffer:
                    console.handle(record)

        # flush what we have stored from the plugin initialization
        _mem_handler.flush()
        _logging_started = True


def flush():
    """Flushes memory logger to console"""
    console = logging.StreamHandler()
    console.setFormatter(_mem_handler.formatter)
    logger = logging.getLogger()
    logger.addHandler(console)
    if len(_mem_handler.buffer) > 0:
        for record in _mem_handler.buffer:
            console.handle(record)
    _mem_handler.flush()


# Set our custom logger class as default
logging.setLoggerClass(FlexGetLogger)
