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
 * Validate quotas on a user or a client.ID of an API key at an API proxy level
 *
 * @param r {Request} HTTP request object
 * @returns {int} HTTP response
 */
async function validateQuota(r) {
    // Generate zone names to find quota meta and remaining
    let userId = r.variables.x_user_id;
    const consumerId = userId !== '' ? userId : '';
    const consumerType = userId !== '' ? USER : CLN
    r.variables.quota_zone = _getQuotaZoneName(r, consumerType);

    // Get quota remaining value from the key/value store in the quota zone
    r.log('validating quota: ' + consumerId + ', ' + r.variables.quota_zone);
    let res = 0;
    try {
        res = await _getValWithKey(r, r.variables.quota_zone, consumerId);
    } catch (e) {
        r.error('quota not found: ' + e);
        r.return(404);
        return;
    }
    const dat = res.split(',');
    const now = new Date().getTime();
    r.variables.quota = Number(dat[0]);
    r.variables.quota_remaining = Number(dat[1]); // no trim to reduct time complexity
    r.variables.quota_exp = Number(dat[2]);
    r.variables.quota_period = dat[3];
    r.variables.quota_after = r.variables.quota_exp - now;
    r.log(" requested-quota: " + r.variables.quota);
    r.log(" quota remaining: " + r.variables.quota_remaining);
    r.log(" quota expiry   : " + r.variables.quota_exp);
    r.log(" quota period   : " + r.variables.quota_period);
    r.log(" quota after    : " + r.variables.quota_after);

    // Check if quota remains
    let msgPrefix = 'quota for ' + consumerId + ': ';
    r.log("now: " + now)
    if (r.variables.quota_remaining > 0) {
        if (r.variables.quota_exp < now) {
            r.error(msgPrefix + 'expired');
            // TODO: send event to reset quota with new expiry time unless quota is disabled.
            r.return(403);
            return;
        }
        r.return(204);
        return;
    } 
    r.error(msgPrefix + 'exhausted');
    // TODO: send event to reset quota with new expiry time unless quota is disabled.
    r.return(403);
}

/**
 * Set quota limit on a user per proxy in key/val zone
 *
 * @param r {Request} HTTP request object
 * @param quotaType {string} quota type
 * @param userId {string} user id (sub)
 * @param proxyName {string} proxy name
 * @param apiMethod {string} api-method
 * @param paymentMethod {string} quota payment method
 * @param quotaLimit {string} quota limit
 * @returns {string} quota name
 */
function setUserQuotaLimit(
    r, quotaType, userId, proxyName, apiMethod, paymentMethod, quotaLimit, limitPer) {
    // let userQuotaName = ''.concat(
    //     quotaType, ':', proxyName, ':', apiMethod, ':', paymentMethod
    // );

    // // Write quota limit on a user per proxy in key/value store
    // let now = r.variables.time_local;
    // r.variables.user_id_quota_name = userId + ':' + userQuotaName;
    // r.variables.user_quota_limit = quotaLimit;
    // r.variables.user_quota_remaining = quotaLimit;
    // r.variables.user_quota_start_time = now;
    // r.variables.user_quota_expiry_time = _getExpiryTime(now, limitPer);

    // TODO: write quota limit on a user per proxy in remote data store
    r.return(201);
}

/**
 * Get expiry time from start time once quota limit is set
 *
 * @param r {long} start time
 * @param r {string} limit per min, hour, day, or month
 * @returns {long} expiry time
 * @private
*/
function _getExpiryTime(now, limitPer) {
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

// Quota Limiting Request: Group or User Level Quota Decrement
//
function decreaseQuota(r) {
    r.log('quota decrement for ' + r.variables.user_id_quota_name);

    // TODO: stand-alone quota decrement
    if (r.variables.quota_remaining) {
        r.variables.quota_remaining--;
    }
    r.return(204);

    // TODO: remote quota decrement
    // let uri = '/quotas/decrement/';
    // let key = r.variables.x_user_id + ':' + r.variables.proxy_name;
    // if (!r.variables.x_user_id) {
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

/**
 * Get quota zone name
 *
 * @param r {Request} HTTP request object
 * @param consumerType {string} consumer type: USR, or CLN for client.ID
 * @returns {string} quota zone name to find key/val from key/val store
 * @private
 */
function _getQuotaZoneName(r, consumerType) {
    let readWrite = ''
    switch(r.method) {
        case 'GET':
            readWrite = 'read';
            break;
        case 'POST':
        case 'PUT':
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

// https://github.com/nginx/njs-examples#setting-keyval-using-a-subrequest-http-api-set-keyval
async function set_keyval(r, zoneName, key, val) {
    let method = r.args.method ? r.args.method : 'PATCH';
    let queryParam = '?{'.concat(key, ':', val, '}');
    let res = await r.subrequest(
        NGINX_PLUS_KEY_VAL_URI + zoneName + '?{' + queryParam,
        {method}
    );

    if (res.status >= 300) {
        r.return(res.status, res.responseBody);
        return;
    }
    r.return(200);
}

/**
 * Get value from key/value store
 *
 * @param r {Request} HTTP request object
 * @param zoneName {string} zone name (e.g., quota zone)
 * @param keyName {string} key of k/v store (e.g., sub, client-id per api key)
 * @param apiMethod {string} api-method
 * @returns value {string} value of k/v store
 * @private
 */
async function _getValWithKey(r, zoneName, keyName) {
    const uri = NGINX_PLUS_KEY_VAL_URI + zoneName;
    const queryParam = '?key=' + keyName;
    let resp = await ngx.fetch(NGINX_PLUS_HOST_PORT + uri + queryParam);
    if (!resp.ok) {
        throw 'No data for the key of ' + keyName + 'in the ' + zoneName;
    }
    const data = await resp.json();
    return data[keyName];
}

export default {
    decreaseQuota,
    setUserQuotaLimit,
    create_keyval,
    set_keyval,
    validateQuota
}
