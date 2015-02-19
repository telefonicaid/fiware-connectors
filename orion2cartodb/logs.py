import logging
import yaml

logger = logging.getLogger('orion2cartodb')
console_handler = logging.StreamHandler()


class ColorFormatter(logging.Formatter):
    def color(self, level=None):
        codes = {\
            None:       (0,   0),
            'DEBUG':    (0,   2), # gris
            'INFO':     (0,   0), # normal
            'WARNING':  (1,  34), # azul
            'ERROR':    (1,  31), # rojo
            'CRITICAL': (1, 101), # negro, fondo rojo
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