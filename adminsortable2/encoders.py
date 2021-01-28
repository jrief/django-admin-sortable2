from django.core.serializers.json import DjangoJSONEncoder

try:
    from hashid_field import Hashid
    HAS_HASHID = True
except ImportError:
    HAS_HASHID = False
    pass

class HashidJSONEncoder(DjangoJSONEncoder):
        def default(self, o):
            if isinstance(o, Hashid):
                return str(o)
            return super().default(o)
