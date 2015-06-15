"""
This module is part of Orion2GoogleSpreadsheet project.

Contains functionality used by Orion2GoogleSpreadsheet to normalize strings
when parsing attributes from received data.
"""

import unicodedata
import string
import logs


# Normalize strings
def string_normalizer(message):
    try:
        # Convert to unicode format
        message = message.decode()

        # Lower-case
        message = message.lower()

        # Replace some characters
        message = message.replace('.', '_')
        message = message.replace(' ', '_')
        message = message.replace(':', '_')

        # Get NFKD unicode format
        message = unicodedata.normalize('NFKD', message)

        # Delete not ascii_letters
        message = ''.join(x for x in message if x in string.ascii_letters or x == "_" or x.isdigit())
    except:
        logs.logger.warn("An error occurred while trying to normalize string")
        return ""

    # Return normalized string
    return message