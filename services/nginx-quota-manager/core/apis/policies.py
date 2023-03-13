"""Business Logic for Rate Limit Policy Configuration API in Control Plane"""

from core.common.constants import RateLimitLevel as Level, RateLimitPer as Per
from core.common.utils import data_not_found, data_already_exist


class RateLimitPolicy:
    """Business Logic for Rate Limiter Policy API"""

    def __init__(self, namespace=None):
        self.rows = {}
        self.names = set()
        self.namespace = namespace
        self._set_default_data()

    def list(self):
        """Get list of rate-limit policies"""
        return list(self.rows.values()), 200

    def get(self, id):
        """Get a rate-limit policy"""
        if id not in self.rows:
            return data_not_found(f"ID ({id})", self.namespace)
        return self.rows[id], 200

    def post(self, data):
        """Create a new rate-limit policy"""
        if 'name' not in data:
            return data_not_found(f"ID ({id})", self.namespace)

        if data['name'] in self.names:
            return data_already_exist(data['name'], self.namespace)

        id = len(self.rows) + 1
        return self._upsert(id, data), 201

    def put(self, id, data):
        """Update a rate-limit policy"""
        if id not in self.rows:
            return data_not_found(f"ID ({id})", self.namespace)
        return self._upsert(id, data), 200

    def _upsert(self, id, data):
        """Create or Update a rate-limit policy"""
        data['id'] = id
        self.rows[id] = data
        self.names.add(data['name'])
        return data

    def delete(self, id):
        """Delete one of rate-limit policies"""
        if id not in self.rows:
            return data_not_found(f"ID ({id})", self.namespace)

        del self.rows[id]
        return {}, 204

    def _set_default_data(self):
        self.post({'id': 1, 'name': 'global-level-rate-limit',
                   'level': Level.GLOBAL, 'rate': Per.SEC, 'req_cnt': 5})
        self.post({'id': 2, 'name': 'user-level-rate-limit',
                   'level': Level.USER, 'rate': Per.SEC, 'req_cnt': 5})
