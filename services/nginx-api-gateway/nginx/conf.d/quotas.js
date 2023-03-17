/*
 *  Copyright 2023 F5, Inc.
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */


/**
 * Validate quotas on a user, a group or a global mode
 *
 * @param r {Request} HTTP request object
 * @returns {int} HTTP response
 */
function validate(r) {
    r.error("QUOTA " + r.variables.quota_remaining);
    if (!r.variables.quota_remaining) {
        r.return(401);
    } else if (r.variables.quota_remaining >= 0) {
        r.return(204);
    } else {
        r.return(403);
    }
}

// Quota Limiting Request: Group or User Level Quota Decrement
//
function decrement(r) {
    let uri = '/quotas/decrement/';
    let key = r.variables.x_user_id + ':' + r.variables.proxy_name;
    if (!r.variables.x_user_id) {
        uri += 'group';
    } else {
        uri += 'users/' + key;
    }
    r.subrequest(uri, function (res) {
        var body = JSON.parse(res.responseBody);
        r.variables.quota_limit = parseInt(body.quota_limit);
        r.variables.quota_remaining = parseInt(body.quota_remaining);
        r.headersOut['X-Quota-Limit'] = parseInt(body.quota_limit);
        r.headersOut['X-Quota-Remaining'] = parseInt(body.quota_remaining);
        if (res.status == 404) {
            r.return(500)
        } else if (res.status == 200) {
            r.return(200)
        } else { // 429
            r.return(403)
        }
    });
}

export default {
    decrement,
    validate
}
