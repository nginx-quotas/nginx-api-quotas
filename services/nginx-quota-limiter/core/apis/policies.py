"""Business Logic for Quota Limit Policy Configuration API in Control Plane"""

from core.common.constants import QuotaLimitLevel as Level, QuotaLimitPer as Per
from core.common.utils import data_not_found, data_already_exist


class QuotaLimitPolicy:
    """Business Logic for Quota Limiter Policy API"""

    def __init__(self, namespace=None):
        self.rows = {}
        self.names = set()
        self.namespace = namespace
        self._set_default_data()

    def list(self):
        """Get list of quota-limit policies"""
        return list(self.rows.values()), 200

    def get(self, id):
        """Get a quota-limit policy"""
        if id not in self.rows:
            return data_not_found(f"ID ({id})", self.namespace)
        return self.rows[id], 200

    def post(self, data):
        """Create a new quota-limit policy"""
        if 'name' not in data:
            return data_not_found(f"ID ({id})", self.namespace)

        if data['name'] in self.names:
            return data_already_exist(data['name'], self.namespace)

        id = len(self.rows) + 1
        return self._upsert(id, data), 201

    def put(self, id, data):
        """Update a quota-limit policy"""
        if id not in self.rows:
            return data_not_found(f"ID ({id})", self.namespace)
        return self._upsert(id, data), 200

    def _upsert(self, id, data):
        """Create or Update a quota-limit policy"""
        data['id'] = id
        self.rows[id] = data
        self.names.add(data['name'])
        return data

    def delete(self, id):
        """Delete one of quota-limit policies"""
        if id not in self.rows:
            return data_not_found(f"ID ({id})", self.namespace)

        del self.rows[id]
        return {}, 204

    def _set_default_data(self):
        self.post({'id': 1, 'name': 'group-level-quota-limit',
                   'level': Level.GROUP, 'rate': Per.SEC, 'req_cnt': 5})
        self.post({'id': 2, 'name': 'user-level-quota-limit',
                   'level': Level.USER, 'rate': Per.SEC, 'req_cnt': 5})
