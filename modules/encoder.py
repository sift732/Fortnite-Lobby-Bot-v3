from enum import Enum
from json import JSONEncoder

import rebootpy


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            if isinstance(obj, rebootpy.Platform):
                return str(obj.value).upper()
            return obj.name.upper()
        if isinstance(obj, type):
            return obj.__name__
        return None
