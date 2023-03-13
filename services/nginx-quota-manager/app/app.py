"""Rate Limiter Service API App"""

from flask import Flask
from flask_restx import Api, Resource
from os import environ

from core.apis.config import RateLimitConfig
from core.apis.decrement import RateLimitDecrement
from core.apis.policies import RateLimitPolicy
from core.apis.status import RateLimitStatus
from core.models.policies import (
    req_api_model as policies_req_api_model,
    res_api_model as policies_res_api_model
)
from core.models.rate_limits import (
    req_api_model as ratelimit_req_api_model,
    res_api_model as ratelimit_res_api_model
)
from core.controller.rate_limiter import RateLimiter


# --------------------------------------------------------------------------- #
#                                                                             #
#                           -  App Initialization  -                          #
#                                                                             #
#   Create app, name space, API request/response models, API access objects:  #
#                                                                             #
#     1) control plane: rate-limit policy for administrator                   #
#        - This is not integrated with data plane yet.                        #
#                                                                             #
#     2) data plane: rate-limiter configuration and request per globa/user    #
#        - ns_config   : configuring rate-limit                               #
#        - ns_decrement: rate-limit request                                   #
#        - ns_status   : check rate-limit status                              #
#                                                                             #
# --------------------------------------------------------------------------- #

app = Flask(__name__)

api = Api(app, version='1.0', title='Rate Limiter Service API',
          description='APIs for managing policies and user/global rate-limits')

ns_policy = api.namespace(
    'ratelimits/policies',
    description='Rate Limit Policies for Control Plane'
)
ns_config = api.namespace(
    'ratelimits',
    description='Rate Limit Config for Data Plane'
)
ns_decrement = api.namespace(
    'ratelimits',
    description='Rate Limit Request Per Global or User'
)
ns_status = api.namespace(
    'ratelimits/status',
    description='Rate Limiter Status for All Buckets'
)

policy_req_model = api.model('policies-request', policies_req_api_model())
policy_res_model = api.model('policies-response', policies_res_api_model())
limit_req_model = api.model('ratelimit-request', ratelimit_req_api_model())
limit_res_model = api.model('ratelimit-response', ratelimit_res_api_model())

policies_api = RateLimitPolicy(ns_policy)
limiter = RateLimiter()
config_api = RateLimitConfig(limiter, ns_config)
decrement_api = RateLimitDecrement(limiter, ns_decrement)
status_api = RateLimitStatus(limiter, ns_decrement)


# --------------------------------------------------------------------------- #
#                                                                             #
#                         -  Control Plane APIs  -                            #
#                                                                             #
#   Create, update, get and delete rate-limit policies for administrator.     #
#                                                                             #
# --------------------------------------------------------------------------- #

@ns_policy.route('')
@ns_policy.response(409, 'The policy of rate-limit already exists.')
class ListPostPolicyAPI(Resource):
    """Rate Limit API to list policies and create a policy.

    It is routed to the endpoint of '{{FQDN}}/rate-limits-policies'.
    """
    @ns_policy.marshal_list_with(policy_res_model, code=200)
    def get(self):
        """Get all list of rate-limit policies"""
        return policies_api.list()

    @ns_policy.expect(policy_req_model)
    @ns_policy.marshal_with(policy_res_model, code=201)
    def post(self):
        """Create a new rate-limit policy"""
        return policies_api.post(api.payload)


@ns_policy.route('/<int:id>')
@ns_policy.response(404, 'Unable to find the policy ID of rate-limit.')
@ns_policy.response(409, 'The policy of rate-limit already exists.')
@ns_policy.param('id', 'Please enter a policy ID of rate-limit.')
class GetPutDelPolicyAPI(Resource):
    """Rate Limit API to get, update and delete a policy.

    It is routed to the endpoint of '{{FQDN}}/rate-limits-policies/<int:id>'.
    """
    @ns_policy.marshal_with(policy_res_model, code=200)
    def get(self, id):
        """Read a rate-limit policy"""
        return policies_api.get(id)

    @ns_policy.expect(policy_req_model)
    @ns_policy.marshal_with(policy_res_model, code=200)
    def put(self, id):
        """Update a rate-limit policy"""
        return policies_api.put(id, api.payload)

    @ns_policy.response(204, 'deleted')
    def delete(self, id):
        """Delete a rate-limit policy"""
        return policies_api.delete(id)


# --------------------------------------------------------------------------- #
#                                                                             #
#                            -  Data Plane APIs  -                            #
#                                                                             #
#  Configure rate-limiter policy, and process rate-limit request:             #
#                                                                             #
#    1) Configuring rate-limit                                                #
#       - global level: configure rate-limit policy for entire system         #
#       - a user level: configure rate-limit policy per each user             #
#                                                                             #
#    2) Processing rate-limit                                                 #
#       - global level: request rate-limit for entire system                  #
#       - a user level: request rate-limit for an user                        #
#                                                                             #
#    3) Check rate-limit status                                               #
#       - all list    : check quota remaining from global/user level limiter  #
#       - global level: check quota remaining from global level limiter       #
#       - a user level: check quota remaining from user level limiter         #
#                                                                             #
#   Note:                                                                     #
#                                                                             #
#    + The APIs are called by API gateway instead of each app's biz logic     #
#      because of the following reasons:                                      #
#      - Easy to set up rate-limit policy in data-plane without implementing  #
#        the API calls per each app codes by just configuration.              #
#      - Easy to change different policies for each API endpoint.             #
#                                                                             #
# --------------------------------------------------------------------------- #

@ns_config.route('/config/global')
@ns_config.response(404, 'Unable to find a global rate-limit configuration.')
@ns_config.response(409, 'The global rate-limit is already configured.')
class GlobalRateLimitConfigAPI(Resource):
    """Rate Limit API to configure a global rate-limit policy.

    It is routed to the endpoint of '{{FQDN}}/ratelimit-config/global'.

    With this API endpoint, we can configure the global rate-limiter by calling
    the function of configure_global_limit() in the class of RateLimiter.
    """
    @ns_config.marshal_with(limit_res_model, code=200)
    def get(self):
        """Get a global rate-limiter configuration information"""
        return config_api.get()

    @ns_config.expect(limit_req_model)
    @ns_config.marshal_with(limit_res_model, code=200)
    def put(self):
        """Configure a global rate-limiter."""
        return config_api.put(api.payload)

    @ns_config.response(204, 'deleted')
    def delete(self):
        """Delete a global rate-limiter"""
        return config_api.delete()


@ns_config.route('/config/users/<string:id>')
@ns_config.response(404, 'Unable to find a user rate-limit configuration.')
@ns_config.response(409, 'The user rate-limit is already configured.')
@ns_config.param('id', 'Please enter a user ID')
class UserRateLimitConfigAPI(Resource):
    """Rate Limit API to configure a user rate-limit policy.

    It is routed to the endpoint of '{{FQDN}}/ratelimit-config/users/<int:id>'.

    With this API endpoint, we can configure the global rate-limiter by calling
    a function of configure_limit() in the class of RateLimiter. In production,
    the endpoint of /login of OIDC workflow can call this function rather than
    implementing the administrative feature to save the cost of development and
    maintenance. Additionally. we can mitigate security attacks based on using
    the OIDC integration.
    """
    @ns_config.marshal_with(limit_res_model, code=200)
    def get(self, id):
        """Get a user's rate-limiter configuration information"""
        return config_api.get(id)

    @ns_config.expect(limit_req_model)
    @ns_config.marshal_with(limit_res_model, code=200)
    def put(self, id):
        """Configure a user's rate-limiter."""
        return config_api.put(api.payload, id)

    @ns_config.response(204, 'deleted')
    def delete(self, id):
        """Delete a user's rate-limiter"""
        return config_api.delete(id)


@ns_decrement.route('/decrement/global')
@ns_decrement.response(429, 'Too many requests.')
class GlobalRateLimitDecrementAPI(Resource):
    """Rate Limit API to process a global rate-limit request.

    It is routed to the endpoint of '{{FQDN}}/ratelimit-decrement/global'.

    With this API endpoint, we can request the global rate-limit by calling the
    function of process_request() in the class of RateLimiter. It returns error
    with a code of 429 which is 'too many requests' if it exceedes the maximum
    amount of quota (a.k.a. X-RateLimit-Limit).

    The fields of X-RateLimit-Limit and X-RateLimit-Remaining are set in the
    response header of api-gateway in this demo repo. The values are included
    in the response body in this app instead for testing purpose.

    IETF RateLimit Header Fields:
    https://tools.ietf.org/id/draft-polli-ratelimit-headers-00.html
    """
    @ns_decrement.marshal_with(limit_res_model, code=429)
    @ns_decrement.marshal_with(limit_res_model, code=200)
    def get(self):
        """Reduce the number of quota remainings globally"""
        return decrement_api.get()


@ns_decrement.route('/decrement/users/<string:id>')
@ns_decrement.response(429, 'Too many requests.')
class UserRateLimitDecrementAPI(Resource):
    """Rate Limit API to process a user rate-limit request.

    It is routed to the URI of '{{FQDN}}/ratelimit-decrement/users/<int:id>'.

    The values of X-RateLimit-Limit and X-RateLimit-Remaining are set in the
    response header of api-gateway such as global rate-limiter. The values are
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
class RateLimitStatusAPI(Resource):
    """Rate Limit API to list quota remaining status of global/user limiter.

    It is routed to the endpoint of '{{FQDN}}/ratelimit-status'.
    """
    @ns_status.marshal_with(limit_res_model, code=200)
    def get(self):
        """Get list of remainig status of global/user rate-limiter"""
        return status_api.list()


@ns_status.route('/global')
@ns_status.response(404, 'Status not found')
class GlobalRateLimitStatusAPI(Resource):
    """Rate Limit API to get quota remaining status of global limiter.

    It is routed to the endpoint of '{{FQDN}}/ratelimit-status/global'.
    """
    @ns_status.marshal_with(limit_res_model, code=200)
    def get(self):
        """Get a remainig status of global rate-limiter"""
        return status_api.get()


@ns_status.route('/users/<string:id>')
@ns_status.response(404, 'Status not found')
class UserRateLimitStatusAPI(Resource):
    """Rate Limit API to get quota remaining status of user limiter.

    It is routed to the endpoint of '{{FQDN}}/ratelimit-status/users/<int:id>'.
    """
    @ns_status.marshal_with(limit_res_model, code=200)
    def get(self, id):
        """Get a remainig status of a user's rate-limiter"""
        return status_api.get(id)


if __name__ == '__main__':
    port = int(environ.get("RATE_LIMITER_PORT", 12000))
    app.run(debug=True, host='0.0.0.0', port=port)
