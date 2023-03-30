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
 * Common constants for quota type
 */
const USER = 'usr';
const CLN = 'cln'; // for client.id per API key

/**
 * Common constants for quota limit-per (a.k.a. rate)
 */
const REQ_MIN = 'r/m';
const REQ_HOUR = 'r/h';
const REQ_DAY = 'r/D';
const REQ_MON = 'r/M';

/**
 * Common constants for seconds per quata limit rate
 */
const MIN_SEC = 60;
const HOUR_SEC = 3600;
const DAY_SEC = 86400;

/**
 * Common constants for postfix of zone name
 */
const NGINX_PLUS_HOST_PORT = 'http://127.0.0.1:8080';
const NGINX_PLUS_KEY_VAL_URI = '/api/7/http/keyvals/';

/**
 * Get quota consumer Id
 *
 * @param r {Request} HTTP request object
 * @returns {string} consumer Id (sub or client-id per api-key)
 */
function quotaConsumerId(r) {
    return r.variables.jwt_claim_sub ? r.variables.jwt_claim_sub : "";
}

/**
 * Get quota zone name
 *
 * @param r {Request} HTTP request object
 * @returns {string} quota zone name to find key/val from key/val store
 */
function quotaZoneName(r) {
    const consumerType = r.variables.jwt_claim_sub !== '' ? USER : CLN
    let readWrite = 'read';
    switch(r.method) {
        case 'POST':
        case 'PUT':
        case 'PATCH':
        case 'DELETE':
            readWrite = 'write';
            break;
    }
    const zoneName = 'quota_'.concat(
        consumerType, '_',
        r.variables.proxy_name, '_',
        r.variables.proxy_ver, '_', 
        readWrite
    );
    return zoneName
}

/**
 * Validate quotas on a user or a client.ID of an API key at an API proxy level
 *
 * @param r {Request} HTTP request object
 * @returns {int} HTTP response
 */
async function validateQuota(r) {
    // Get quota remaining value from the key/value store in the quota zone
    const consumerId = r.variables.jwt_claim_sub ? r.variables.jwt_claim_sub : '';
    r.variables.quota_message = '';
    r.log('validating quota: ' + consumerId + ', ' + r.variables.quota_zone);
    let quotas = 0;
    try {
        quotas = await _getValWithKey(r.variables.quota_zone, consumerId);
    } catch (e) {
        r.variables.quota_status_code = 404;
        r.variables.quota_message = 'quota not found: ' + e;
        r.error(r.variables.quota_message);
        r.return(403);
        return;
    }
    const dat = quotas.split(',');
    const now = new Date().getTime();
    r.variables.quota = Number(dat[0]);
    r.variables.quota_remaining = Number(dat[1]); // no trim to reduce time complexity
    r.variables.quota_exp = Number(dat[2]);
    r.variables.quota_period = dat[3];
    r.variables.quota_after = r.variables.quota_exp - now;

    // Check if quota remains, or if quota is expired.
    let msgPrefix = 'quota for ' + consumerId + ': ';
    r.variables.quota_status_code = 429;
    if (r.variables.quota_remaining > 0) {
        if (r.variables.quota_exp < now) {
            r.variables.quota_message = msgPrefix + 'expired';
            r.error(r.variables.quota_message);
            // TODO: send event to reset quota with new expiry time unless quota is disabled.
            r.return(403);
            return;
        }
        r.variables.quota_status_code = 204;
        r.return(204);
        return;
    } 
    r.variables.quota_message = msgPrefix + 'expired';
    r.error(r.variables.quota_message);
    // TODO: send event to reset quota with new expiry time unless quota is disabled.
    r.return(403);
}

/**
 * Decrease a quota on a user or a client.ID of an API key at an API proxy level
 *
 * @param r {Request} HTTP request object
 * @returns {int} HTTP response
 */
async function decreaseQuota(r) {
    r.log('start quota decrement for ' + r.variables.quota_consumer_id);

    // stand-alone quota decrement
    if (r.variables.quota_remaining) {
        r.variables.quota_remaining--;
    }
    const val =  r.variables.quota.toString().concat(
            ',', r.variables.quota_remaining.toString(),
            ',', r.variables.quota_exp.toString(),
            ',', r.variables.quota_period
    );
    try {
        await _setValWithKey(
            r.variables.quota_zone, 
            r.variables.quota_consumer_id, 
            val
        );
    } catch (e) {
        r.variables.quota_status_code = 500;
        r.variables.quota_message = 'quota decrement failed: ' + e;
        r.error(r.variables.quota_message);

        r.return(403);
        return;
    }
    r.variables.quota_status_code = 204;
    r.log('finished quota-decrement: ' + r.variables.quota_remaining);
    r.return(204);

    // TODO: remote quota decrement
    // let uri = '/quotas/decrement/';
    // let key = r.variables.jwt_claim_sub + ':' + r.variables.proxy_name;
    // if (!r.variables.jwt_claim_sub) {
    //     uri += 'group';
    // } else {
    //     uri += 'users/' + key;
    // }
    // r.subrequest(uri, function (res) {
    //     var body = JSON.parse(res.responseBody);
    //     r.variables.quota_limit = parseInt(body.quota_limit);
    //     r.variables.quota_remaining = parseInt(body.quota_remaining);
    //     r.headersOut['X-User-Quota-Limit'] = parseInt(body.quota_limit);
    //     r.headersOut['X-User-Quota-Remaining'] = parseInt(body.quota_remaining);
    //     if (res.status == 404) {
    //         r.return(500)
    //     } else if (res.status == 200) {
    //         r.return(200)
    //     } else { // 429
    //         r.return(403)
    //     }
    // });
}

/**
 * Get new expiry time when quota is either created or reset.
 *
 * @param r {string} limit per min, hour, day, or month
 * @returns {long} expiry time
 * @private
*/
function _getNewExpiryTime(limitPer) {
    const now = new Date().getTime();
    switch(limitPer) {
        case REQ_MIN: return now + MIN_SEC;
        case REQ_HOUR: return now + HOUR_SEC;
        case REQ_DAY: return now + DAY_SEC;
        case REQ_MON: 
            let after1M = new Date(now);
            after1M = new Date(
                after1M.getFullYear(), after1M.getMonth()+1, after1M.getDate()
            );
            let lAfter1M = after1M.getTime();
            return lAfter1M;
    }
    return 0;
}

/**
 * Get quota name
 *
 * @param r {Request} HTTP request object
 * @returns {string} quota payment method
 * @private
 */
function _setHeadersOut(r, now) {
    // r.headersOut['X-User-Quota-Policy'] = r.variables.user_id_quota_name;
    r.headersOut['X-User-Quota'] = r.variables.quota;
    r.headersOut['X-User-Quota-Remaining'] = r.variables.quota_remaining;
    r.headersOut['X-User-Quota-Reset'] = r.variables.quota_ext - now;
    // r.headersOut['X-Group-Quota-Limit'] = r.variables.group_quota_limit;
    // r.headersOut['X-Group-Quota-Remaining'] = r.variables.group_quota_remaining;
}

async function create_keyval(r, zoneName) {
    let method = r.args.method ? r.args.method : 'POST';
    let res = await r.subrequest(NGINX_PLUS_KEY_VAL_URI + zoneName,
                                 { method, body: r.requestBody});

    if (res.status >= 300) {
        r.return(res.status, res.responseBody);
        return;
    }
    r.return(200);
}

/**
 * Set value into key/value store
 * https://github.com/nginx/njs-examples#setting-keyval-using-a-subrequest-http-api-set-keyval
 *
 * @param r {Request} HTTP request object
 * @param zoneName {string} zone name (e.g., quota zone)
 * @param keyName {string} key of k/v store (e.g., sub, client-id per api key)
 * @param val {string} value of k/v store
 * @private
 */
async function _setValWithKey(zoneName, keyName, val) {
    const uri = NGINX_PLUS_HOST_PORT + NGINX_PLUS_KEY_VAL_URI + zoneName;
    let reqBody = {};
    reqBody[keyName] = val;
    let resp = await ngx.fetch(uri,
        {
            body: JSON.stringify(reqBody), 
            method: 'PATCH'
        }
    );
    if (!resp.ok) {
        const data = await resp.text();
        const errMessage = 'Patch failed for the key of '.concat(
            keyName, ' in the ', zoneName,
            'status: ', resp.status,
            'response: ', data
        )
        throw errMessage;
    }
}

/**
 * Get value from key/value store
 *
 * @param zoneName {string} zone name (e.g., quota zone)
 * @param keyName {string} key of k/v store (e.g., sub, client-id per api key)
 * @returns value {string} value of k/v store
 * @private
 */
async function _getValWithKey(zoneName, keyName) {
    const uri = NGINX_PLUS_KEY_VAL_URI + zoneName;
    const queryParam = '?key=' + keyName;
    let resp = await ngx.fetch(NGINX_PLUS_HOST_PORT + uri + queryParam);
    if (!resp.ok) {
        throw 'No data for the key of ' + keyName + 'in the ' + zoneName;
    }
    const data = await resp.json();
    return data[keyName];
}

/**
 * Return quota error response
 *
 * @param r {Request} HTTP request object
 * @returns {int} HTTP response
 * @private
 */
function error(r) {
    r.return(
        parseInt(r.variables.quota_status_code), 
        '{"message": "' + r.variables.quota_message + '"}\n'
    )
}

export default {
    decreaseQuota,
    error,
    quotaConsumerId,
    quotaZoneName,
    create_keyval,
    validateQuota
}
