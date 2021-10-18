import logging
import sys

# DEFAULT
DEFAULT_LOG_BASIC_FORMATTER = '[%(levelname)-8s]: %(message)s '
DEFAULT_LOG_VERBA_FORMATTER = '%(relativeCreated)dms [%(levelname)-8s]: %(message)s '
DEFAULT_LOG_VERBB_FORMATTER = lambda x: '%(relativeCreated)dms - ({}-%(name)s) [%(levelname)-8s]: %(message)s '.format(x)
DEFAULT_LOG_VERBC_FORMATTER = '%(relativeCreated)dms - (%(name)s) [%(levelname)-8s]: %(message)s '
DEFAULT_FMT_TIME = '%H:%M:%S'


class CountLogger(logging.getLoggerClass()):
    """ Create a new logger class that count warnings and errors.

    The counter is incrrease each time a warning or error are logged. In all
    cases the super methods are used.
    The `counter` is stored has a dictionnary. Use `counter['warning']` to
    get the value.
    """

    def __init__(self, name):
        """ Overload base class init.
        """
        super().__init__(name)
        # store counters in a dict
        self.counter = {'warning': 0, 'error': 0, 'critical': 0}

    def warning(self, msg, *args, **kwargs):
        self.counter['warning'] += 1
        super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.counter['error'] += 1
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.counter['critical'] += 1
        super().critical(msg, *args, **kwargs)

    def reset_counter(self):
        """ Manually reset the counter.

        As the logger object are instanciated once. If the conversion is call
        serveral time the counter need to be reset.
        """
        self.counter.update({key: 0 for key in self.counter})


class customLogger:
    """ Basic custom Logger management.

    It allows to load logger, remove console/file logger, create console/file
    logger.
    """

    def __init__(self, loggerName='custom'):
        """ Load logger with loggerName ID and set level to DEBUG.
        """
        logging.setLoggerClass(CountLogger)
        self.rootLogger = logging.getLogger(loggerName)
        self.rootLogger.setLevel(logging.DEBUG)
        # Manually reset all logger counters at each run
        self.rootLogger.reset_counter()
        for log_name, log_obj in logging.Logger.manager.loggerDict.items():
            if 'amc2moodle' in log_name:
                logging.getLogger(log_name).reset_counter()

    def removeConsoleLogger(self):
        """ Remove all console Loggers.
        """
        for hdlr in self.rootLogger.handlers[:]:
            if isinstance(hdlr, logging.StreamHandler):
                self.rootLogger.removeHandler(hdlr)

    def removeFileLogger(self):
        """ Remove all file loggers.
        """
        for hdlr in self.rootLogger.handlers[:]:
            if isinstance(hdlr, logging.FileHandler):
                self.rootLogger.removeHandler(hdlr)

    def setupConsoleLogger(self, verbositylevel=0, silent=False, txtinfo=None):
        """ Create a console Logger.

        It defines the
        - level of verbosity (`verbositylevel` from 0 to 2)
        - `silent` mode (overrides verbosity)
        - a specific word in the log message (using `txtinfo`)
        """
        # Remove all console Logger
        self.removeConsoleLogger()
        # Create Stream handler
        sH = logging.StreamHandler(stream=sys.stdout)
        # Create basic logging level
        basicLogLevel = logging.INFO
        # Silent mode overrides verbosity level
        if silent:
            verbositylevel = 0
            basicLogLevel = logging.ERROR

        if verbositylevel == 0:
            # Basic verbosity (no DEBUG, defaut)
            sH.setFormatter(
                logging.Formatter(fmt=DEFAULT_LOG_BASIC_FORMATTER))
            sH.setLevel(basicLogLevel)
        elif verbositylevel == 1:
            # First level of verbosity (classic DEBUG level)
            sH.setLevel(logging.DEBUG)
            sH.setFormatter(
                logging.Formatter(fmt=DEFAULT_LOG_VERBA_FORMATTER))
        else:
            # Second level of verbosity (DEBUG level with details)
            sH.setLevel(logging.DEBUG)
            if txtinfo is not None:
                fmtCustom = DEFAULT_LOG_VERBB_FORMATTER(txtinfo)
            else:
                fmtCustom = DEFAULT_LOG_VERBC_FORMATTER
            sH.setFormatter(logging.Formatter(fmt=fmtCustom))
        # Add handler to the logger
        self.rootLogger.addHandler(sH)

    def setupFileLogger(self, filename, verbositylevel=2, silent=False,
                        txtinfo=None):
        """ Create a file Logger.

        The new file logger is created with
        - the file specified by `filename`
        - level of verbosity (`verbositylevel` from 0 to 2)
        - `silent` mode (overrides verbosity)
        - a specific word in the log message (using `txtinfo`)
        """
        # Remove all file Loggers
        self.removeFileLogger()
        # Create basic logging level
        basicLogLevel = logging.INFO
        # Silent mode overrides verbosity level
        if silent:
            verbositylevel = 0
            basicLogLevel = logging.ERROR
        # Create file handler
        fH = logging.FileHandler(filename)
        if verbositylevel == 0:
            # Basic verbosity (no DEBUG)
            fH.setFormatter(logging.Formatter(
                fmt=DEFAULT_LOG_BASIC_FORMATTER
            ))
            fH.setLevel(basicLogLevel)
        elif verbositylevel == 1:
            # First level of verbosity (classic DEBUG level)
            fH.setLevel(logging.DEBUG)
            fH.setFormatter(logging.Formatter(fmt=DEFAULT_LOG_VERBA_FORMATTER))
        else:
            # Second level of verbosity (DEBUG level with details, default)
            fH.setLevel(logging.DEBUG)
            if txtinfo is not None:
                fmtCustom = DEFAULT_LOG_VERBB_FORMATTER(txtinfo)
            else:
                fmtCustom = DEFAULT_LOG_VERBC_FORMATTER
            fH.setFormatter(logging.Formatter(fmt=fmtCustom))
        # add handler to the logger
        self.rootLogger.addHandler(fH)

    def getLogger(self):
        """ Return root Logger.
        """
        return self.rootLogger
