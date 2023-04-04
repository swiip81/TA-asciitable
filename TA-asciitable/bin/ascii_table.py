import sys
import os
import logging
import time
import splunk
from collections import OrderedDict
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
from beautifultable import BeautifulTable

@Configuration()
class ascii_table(StreamingCommand):
    style = Option(name='style', require=False, default="BeautifulTable.STYLE_DEFAULT")
    maxwidth = Option(name='maxwidth', require=False, default=150)
    alignment = Option(name='alignment', require=False, default="BeautifulTable.ALIGN_LEFT")
    def stream(self, events):
        def setupLogging():
            # Define the logger
            logger = logging.getLogger(__name__)
            SPLUNK_HOME = os.environ['SPLUNK_HOME']
            LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
            LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
            LOGGING_STANZA_NAME = 'python'
            LOGGING_FILE_NAME = "asciitable.log"
            BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
            LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
            splunk_log_handler = logging.handlers.RotatingFileHandler(
                os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
            splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
            logger.addHandler(splunk_log_handler)
            splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
            return logger

        output = OrderedDict()
        # We will init only one row per stream, and we force time to be now()
        output["_time"] = time.time()
        table = BeautifulTable(max_width=int(self.maxwidth))
        if not self.style.startswith("BeautifulTable."):
            # force display of error in splunk to suggest correct styles
            table.set_style(str(self.style))
        table.set_style(eval(self.style))
        if not self.alignment.startswith("BeautifulTable."):
            # force display of error in splunk to suggest correct alignment
            sys.exit('* beautifultable.ALIGN_LEFT * beautifultable.ALIGN_CENTER * beautifultable.ALIGN_RIGHT')
        table.columns.alignment = eval(self.alignment)
        build_titles = []
        init = 0
        for event in events:
            build_values = []
            for fields in event:
                if not fields.startswith("_") or fields == "_time":
                    if init == 0:
                        # during the first event we build the field names list
                        build_titles.append(fields)
                    build_values.append(event[fields])
            table.rows.append(build_values)
            if init == 0:
                table.columns.header = build_titles
                #output["event"] = str(events)
                init = 1
        output["result_of_the_table"] = str(table)
        yield output

dispatch(ascii_table, sys.argv, sys.stdin, sys.stdout, __name__)
