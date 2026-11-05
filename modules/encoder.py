import enum
import importlib
from json import JSONEncoder

nextcord = importlib.import_module('nextcord')
rebootpy = importlib.import_module('rebootpy')


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        actual_class = getattr(obj, '_actual_enum_cls_', obj.__class__)
        discord_enum = getattr(nextcord, 'Enum', None)
        if isinstance(discord_enum, type) and isinstance(actual_class, type) and issubclass(actual_class, discord_enum):
            return obj.name.lower()
        if isinstance(obj, rebootpy.Platform):
            return str(obj.value).upper()
        if isinstance(obj, enum.Enum):
            return obj.name.upper()
        if isinstance(obj, type):
            return obj.__name__
        return super().default(obj)
