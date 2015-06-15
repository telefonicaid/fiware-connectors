import logging
import yaml

logger = logging.getLogger('Orion2GoogleSpreadsheet')
console_handler = logging.StreamHandler()


class ColorFormatter(logging.Formatter):
    def color(self, level=None):
        codes = {\
            None:       (0,   0),
            'DEBUG':    (0,   2), # grey
            'INFO':     (0,   0), # black
            'WARNING':  (1,  34), # blue
            'ERROR':    (1,  31), # red
            'CRITICAL': (1, 101), # black, red background
            }
        return (chr(27)+'[%d;%dm') % codes[level]

    def format(self, record):
        retval = logging.Formatter.format(self, record)
        return self.color(record.levelname) + retval + self.color()


def config_log():
    file = open("configlog.yaml")
    properties = yaml.load(file)
    logger.setLevel(logging.DEBUG)
    console_handler.setLevel(properties["log_level"])
    console_handler.setFormatter(ColorFormatter(properties["log_format"]))
    logger.addHandler(console_handler)
