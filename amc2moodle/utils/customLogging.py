import logging
import sys

# DEFAULT
DEFAULT_LOG_BASIC_FORMATTER = '[%(levelname)-8s]: %(message)s '
DEFAULT_LOG_VERBA_FORMATTER = '%(relativeCreated)dms [%(levelname)-8s]: %(message)s '
DEFAULT_LOG_VERBB_FORMATTER = lambda x : '%(relativeCreated)dms - ({}-%(name)s) [%(levelname)-8s]: %(message)s '.format(x)
DEFAULT_LOG_VERBC_FORMATTER = '%(relativeCreated)dms - (%(name)s) [%(levelname)-8s]: %(message)s '
DEFAULT_FMT_TIME = '%H:%M:%S'


class customLogger:
    """ 
    Basic custom Logger management (load logger, remove consol/file logger, create console/file logger)
    """

    def __init__(self,
        loggerName='custom'):
        """
        Load logger with loggerName ID and set level to DEBUG
        """
        self.rootLogger = logging.getLogger(loggerName)
        self.rootLogger.setLevel(logging.DEBUG)

    def removeConsoleLogger(self):
        """
        Remove all console Loggers
        """
        for hdlr in self.rootLogger.handlers[:]:
            if isinstance(hdlr,logging.StreamHandler):
                self.rootLogger.removeHandler(hdlr)
    
    def removeFileLogger(self):
        """
        Remove all file loggers
        """
        for hdlr in self.rootLogger.handlers[:]:
            if isinstance(hdlr,logging.FileHandler):
                self.rootLogger.removeHandler(hdlr) 


    def setupConsoleLogger(self,
        verbositylevel = 0,
        silent = False,
        txtinfo = None):
        """
        Create a console Logger with
        - level of verbosity (verbositylevel from 0 to 2)
        - silent mode (overrides verbosity)
        - a specific word in the log message (using txtinfo)
        """
        #remove all console Logger
        self.removeConsoleLogger()
        #create Stream handler
        sH = logging.StreamHandler(stream=sys.stdout)
        #create basic logging level
        basicLogLevel = logging.INFO
        #silent mode overrides verbosity level
        if silent:
            verbositylevel = 0
            basicLogLevel = logging.ERROR
        #
        if verbositylevel == 0:
            #basic verbosity (no DEBUG, defaut)
            sH.setFormatter(logging.Formatter(
                fmt=DEFAULT_LOG_BASIC_FORMATTER
            ))
            sH.setLevel(basicLogLevel)
        elif verbositylevel == 1:
            #first level of verbosity (classic DEBUG level)
            sH.setLevel(logging.DEBUG)
            sH.setFormatter(
                logging.Formatter(fmt=DEFAULT_LOG_VERBA_FORMATTER))
        else:
            #second level of verbosity (DEBUG level with details)
            sH.setLevel(logging.DEBUG)
            if txtinfo is not None:
                fmtCustom = DEFAULT_LOG_VERBB_FORMATTER(txtinfo)
            else:
                fmtCustom = DEFAULT_LOG_VERBC_FORMATTER
            sH.setFormatter(logging.Formatter(fmt=fmtCustom))
        # add handler to the logger
        self.rootLogger.addHandler(sH)           


    def setupFileLogger(self,
        filename,
        verbositylevel = 2,
        silent = False,
        txtinfo = None):
        """
        Create a file Logger with
        - the file specified by filename
        - level of verbosity (verbositylevel from 0 to 2)
        - silent mode (overrides verbosity)
        - a specific word in the log message (using txtinfo)
        """
        #remove all file Loggers
        self.removeFileLogger()
        #create basic logging level
        basicLogLevel = logging.INFO
        #silent mode overrides verbosity level
        if silent:
            verbositylevel = 0
            basicLogLevel = logging.ERROR
        #create file handler
        fH = logging.FileHandler(filename)
        if verbositylevel == 0:
            #basic verbosity (no DEBUG)
            fH.setFormatter(logging.Formatter(
                fmt=DEFAULT_LOG_BASIC_FORMATTER
            ))
            fH.setLevel(basicLogLevel)
        elif verbositylevel == 1:
            #first level of verbosity (classic DEBUG level)
            fH.setLevel(logging.DEBUG)
            fH.setFormatter(logging.Formatter(fmt=DEFAULT_LOG_VERBA_FORMATTER))
        else:
            #second level of verbosity (DEBUG level with details, default)
            fH.setLevel(logging.DEBUG)
            if txtinfo is not None:
                fmtCustom = DEFAULT_LOG_VERBB_FORMATTER(txtinfo)
            else:
                fmtCustom = DEFAULT_LOG_VERBC_FORMATTER
            fH.setFormatter(logging.Formatter(fmt=fmtCustom))
        # add handler to the logger
        self.rootLogger.addHandler(fH)

    def getLogger(self):
        """
        Return root Logger
        """
        return self.rootLogger


