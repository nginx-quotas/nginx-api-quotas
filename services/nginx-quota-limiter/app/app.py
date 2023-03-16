"""Quota Limiter Service API App"""

from flask import Flask
from flask_restx import Api, Resource
from os import environ

from core.apis.config import QuotaLimitConfig
from core.apis.decrement import QuotaLimitDecrement
from core.apis.policies import QuotaLimitPolicy
from core.apis.status import QuotaLimitStatus
from core.models.policies import (
    req_api_model as policies_req_api_model,
    res_api_model as policies_res_api_model
)
from core.models.quota_limits import (
    req_api_model as quotalimit_req_api_model,
    res_api_model as quotalimit_res_api_model
)
from core.controller.quota_limiter import QuotaLimiter


# --------------------------------------------------------------------------- #
#                                                                             #
#                           -  App Initialization  -                          #
#                                                                             #
#   Create app, name space, API request/response models, API access objects:  #
#                                                                             #
#     1) control plane: quota-limit policy for administrator                  #
#        - This is not integrated with data plane yet.                        #
#                                                                             #
#     2) data plane: quota-limiter configuration and request per group/user   #
#        - ns_config   : configuring quota-limit                              #
#        - ns_decrement: quota-limit request                                  #
#        - ns_status   : check quota-limit status                             #
#                                                                             #
# --------------------------------------------------------------------------- #

app = Flask(__name__)

api = Api(app, version='1.0', title='Quota Limiter Service API',
          description='APIs for managing policies and user/group quota-limits')

ns_policy = api.namespace(
    'quotalimits/policies',
    description='Quota Limit Policies for Control Plane'
)
ns_config = api.namespace(
    'quotalimits',
    description='Quota Limit Config for Data Plane'
)
ns_decrement = api.namespace(
    'quotalimits',
    description='Quota Limit Request Per Group or User'
)
ns_status = api.namespace(
    'quotalimits/status',
    description='Quota Limiter Status for All Buckets'
)

policy_req_model = api.model('policies-request', policies_req_api_model())
policy_res_model = api.model('policies-response', policies_res_api_model())
limit_req_model = api.model('quotalimit-request', quotalimit_req_api_model())
limit_res_model = api.model('quotalimit-response', quotalimit_res_api_model())

policies_api = QuotaLimitPolicy(ns_policy)
limiter = QuotaLimiter()
config_api = QuotaLimitConfig(limiter, ns_config)
decrement_api = QuotaLimitDecrement(limiter, ns_decrement)
status_api = QuotaLimitStatus(limiter, ns_decrement)


# --------------------------------------------------------------------------- #
#                                                                             #
#                         -  Control Plane APIs  -                            #
#                                                                             #
#   Create, update, get and delete quota-limit policies for administrator.     #
#                                                                             #
# --------------------------------------------------------------------------- #

@ns_policy.route('')
@ns_policy.response(409, 'The policy of quota-limit already exists.')
class ListPostPolicyAPI(Resource):
    """Quota Limit API to list policies and create a policy.

    It is routed to the endpoint of '{{FQDN}}/quota-limits-policies'.
    """
    @ns_policy.marshal_list_with(policy_res_model, code=200)
    def get(self):
        """Get all list of quota-limit policies"""
        return policies_api.list()

    @ns_policy.expect(policy_req_model)
    @ns_policy.marshal_with(policy_res_model, code=201)
    def post(self):
        """Create a new quota-limit policy"""
        return policies_api.post(api.payload)


@ns_policy.route('/<int:id>')
@ns_policy.response(404, 'Unable to find the policy ID of quota-limit.')
@ns_policy.response(409, 'The policy of quota-limit already exists.')
@ns_policy.param('id', 'Please enter a policy ID of quota-limit.')
class GetPutDelPolicyAPI(Resource):
    """Quota Limit API to get, update and delete a policy.

    It is routed to the endpoint of '{{FQDN}}/quota-limits-policies/<int:id>'.
    """
    @ns_policy.marshal_with(policy_res_model, code=200)
    def get(self, id):
        """Read a quota-limit policy"""
        return policies_api.get(id)

    @ns_policy.expect(policy_req_model)
    @ns_policy.marshal_with(policy_res_model, code=200)
    def put(self, id):
        """Update a quota-limit policy"""
        return policies_api.put(id, api.payload)

    @ns_policy.response(204, 'deleted')
    def delete(self, id):
        """Delete a quota-limit policy"""
        return policies_api.delete(id)


# --------------------------------------------------------------------------- #
#                                                                             #
#                            -  Data Plane APIs  -                            #
#                                                                             #
#  Configure quota-limiter policy, and process quota-limit request:             #
#                                                                             #
#    1) Configuring quota-limit                                                #
#       - group level: configure quota-limit policy for entire system         #
#       - a user level: configure quota-limit policy per each user             #
#                                                                             #
#    2) Processing quota-limit                                                 #
#       - group level: request quota-limit for entire system                  #
#       - a user level: request quota-limit for an user                        #
#                                                                             #
#    3) Check quota-limit status                                               #
#       - all list    : check quota remaining from group/user level limiter  #
#       - group level: check quota remaining from group level limiter       #
#       - a user level: check quota remaining from user level limiter         #
#                                                                             #
#   Note:                                                                     #
#                                                                             #
#    + The APIs are called by API gateway instead of each app's biz logic     #
#      because of the following reasons:                                      #
#      - Easy to set up quota-limit policy in data-plane without implementing  #
#        the API calls per each app codes by just configuration.              #
#      - Easy to change different policies for each API endpoint.             #
#                                                                             #
# --------------------------------------------------------------------------- #

@ns_config.route('/config/group')
@ns_config.response(404, 'Unable to find a group quota-limit configuration.')
@ns_config.response(409, 'The group quota-limit is already configured.')
class GroupQuotaLimitConfigAPI(Resource):
    """Quota Limit API to configure a group quota-limit policy.

    It is routed to the endpoint of '{{FQDN}}/quotalimit-config/group'.

    With this API endpoint, we can configure the group quota-limiter by calling
    the function of configure_group_limit() in the class of QuotaLimiter.
    """
    @ns_config.marshal_with(limit_res_model, code=200)
    def get(self):
        """Get a group quota-limiter configuration information"""
        return config_api.get()

    @ns_config.expect(limit_req_model)
    @ns_config.marshal_with(limit_res_model, code=200)
    def put(self):
        """Configure a group quota-limiter."""
        return config_api.put(api.payload)

    @ns_config.response(204, 'deleted')
    def delete(self):
        """Delete a group quota-limiter"""
        return config_api.delete()


@ns_config.route('/config/users/<string:id>')
@ns_config.response(404, 'Unable to find a user quota-limit configuration.')
@ns_config.response(409, 'The user quota-limit is already configured.')
@ns_config.param('id', 'Please enter a user ID')
class UserQuotaLimitConfigAPI(Resource):
    """Quota Limit API to configure a user quota-limit policy.

    It is routed to the endpoint of '{{FQDN}}/quotalimit-config/users/<int:id>'.

    With this API endpoint, we can configure the group quota-limiter by calling
    a function of configure_limit() in the class of QuotaLimiter. In production,
    the endpoint of /login of OIDC workflow can call this function rather than
    implementing the administrative feature to save the cost of development and
    maintenance. Additionally. we can mitigate security attacks based on using
    the OIDC integration.
    """
    @ns_config.marshal_with(limit_res_model, code=200)
    def get(self, id):
        """Get a user's quota-limiter configuration information"""
        return config_api.get(id)

    @ns_config.expect(limit_req_model)
    @ns_config.marshal_with(limit_res_model, code=200)
    def put(self, id):
        """Configure a user's quota-limiter."""
        return config_api.put(api.payload, id)

    @ns_config.response(204, 'deleted')
    def delete(self, id):
        """Delete a user's quota-limiter"""
        return config_api.delete(id)


@ns_decrement.route('/decrement/group')
@ns_decrement.response(429, 'Too many requests.')
class GroupQuotaLimitDecrementAPI(Resource):
    """Quota Limit API to process a group quota-limit request.

    It is routed to the endpoint of '{{FQDN}}/quotalimit-decrement/group'.

    With this API endpoint, we can request the group quota-limit by calling the
    function of process_request() in the class of QuotaLimiter. It returns error
    with a code of 429 which is 'too many requests' if it exceedes the maximum
    amount of quota (a.k.a. X-QuotaLimit-Limit).

    The fields of X-QuotaLimit-Limit and X-QuotaLimit-Remaining are set in the
    response header of api-gateway in this demo repo. The values are included
    in the response body in this app instead for testing purpose.

    IETF QuotaLimit Header Fields:
    https://tools.ietf.org/id/draft-polli-quotalimit-headers-00.html
    """
    @ns_decrement.marshal_with(limit_res_model, code=429)
    @ns_decrement.marshal_with(limit_res_model, code=200)
    def get(self):
        """Reduce the number of quota remainings grouply"""
        return decrement_api.get()


@ns_decrement.route('/decrement/users/<string:id>')
@ns_decrement.response(429, 'Too many requests.')
class UserQuotaLimitDecrementAPI(Resource):
    """Quota Limit API to process a user quota-limit request.

    It is routed to the URI of '{{FQDN}}/quotalimit-decrement/users/<int:id>'.

    The values of X-QuotaLimit-Limit and X-QuotaLimit-Remaining are set in the
    response header of api-gateway such as group quota-limiter. The values are
    included in the response body in this app instead for testing purpose.

    In production, I recommend the user ID is matched with the `sub` of IdP so
    that we can easily maintain user mgmt., and mitigate threats possibility
    by reusing IdP. In the meantime, I have changed the type of ID from integer
    to string for considering scaling millions of users.
    """
    @ns_decrement.marshal_with(limit_res_model, code=429)
    @ns_decrement.marshal_with(limit_res_model, code=200)
    def get(self, id):
        """Reduce the number of quota remainings per user ID"""
        return decrement_api.get(id)


@ns_status.route('')
@ns_status.response(404, 'Status not found')
class QuotaLimitStatusAPI(Resource):
    """Quota Limit API to list quota remaining status of group/user limiter.

    It is routed to the endpoint of '{{FQDN}}/quotalimit-status'.
    """
    @ns_status.marshal_with(limit_res_model, code=200)
    def get(self):
        """Get list of remainig status of group/user quota-limiter"""
        return status_api.list()


@ns_status.route('/group')
@ns_status.response(404, 'Status not found')
class GroupQuotaLimitStatusAPI(Resource):
    """Quota Limit API to get quota remaining status of group limiter.

    It is routed to the endpoint of '{{FQDN}}/quotalimit-status/group'.
    """
    @ns_status.marshal_with(limit_res_model, code=200)
    def get(self):
        """Get a remainig status of group quota-limiter"""
        return status_api.get()


@ns_status.route('/users/<string:id>')
@ns_status.response(404, 'Status not found')
class UserQuotaLimitStatusAPI(Resource):
    """Quota Limit API to get quota remaining status of user limiter.

    It is routed to the endpoint of '{{FQDN}}/quotalimit-status/users/<int:id>'.
    """
    @ns_status.marshal_with(limit_res_model, code=200)
    def get(self, id):
        """Get a remainig status of a user's quota-limiter"""
        return status_api.get(id)


if __name__ == '__main__':
    port = int(environ.get("RATE_LIMITER_PORT", 12001))
    app.run(debug=True, host='0.0.0.0', port=port)
