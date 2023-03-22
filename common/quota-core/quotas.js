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
 * Common constants for API methods
 */
const API_READ = 'R';
const API_WRITE = 'W';

/**
 * Common constants for quota type
 */
const USER = 'usr';
const CLN = 'cln'; // for client.id per API key
const GLOBAL = 'glo';

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
const MON_SEC = 2678400; // 31 days


/**
 * Get a quota policy
 *
 * @param r {Request} HTTP request object
 * @returns quota policy {object} quota policy object
 */
function getQuotaPolicy(r) {

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
 * @returns {int} HTTP response
 * @private
*/
function _getExpiryTime(now, limitPer) {
    switch(limitPer) {
        case REQ_HOUR: return now + HOUR_SEC;
        case REQ_DAY: return now + DAY_SEC;
        case REQ_MON: return now + MON_SEC; // TODO: calculate secs per each month
    }
    return 0;
}

/**
 * Validate quotas on a user, a group or a global mode
 *
 * @param r {Request} HTTP request object
 * @returns {int} HTTP response
 */
function validateQuota(r) {
    // Generate zone name to find quota meta and status
    let userId = r.variables.x_user_id;
    let zoneNameQuotaMeta = '';
    let zoneNameRemaining = '';
    if (userId !== '') {
        zoneNameQuotaMeta = _getZoneName(r, USER, false);
        zoneNameRemaining = _getZoneName(r, USER, true);
    } else {
        zoneNameQuotaMeta = _getZoneName(r, CLN, false);
        zoneNameRemaining = _getZoneName(r, CLN, true);
    }
    r.log('##### validate quota: ');
    r.log('         zoneNameQuotaMeta: ' + zoneNameQuotaMeta);
    r.log('         zoneNameRemaining: ' + zoneNameRemaining);

    // // Get and set user quota name
    // let userQuotaName = '';
    // if (r.variables.quota_enable_per_user_proxy && 
    //     r.variables.quota_enable_per_user_proxy === '1') {
    //     userQuotaName = _getQuotaName(r, USER, userId, API_ALL);
    // }
    // if (!userQuotaName) {
    //     switch(r.method) {
    //         case 'GET':
    //             if (r.variables.quota_enable_per_user_proxy_read &&
    //                 r.variables.quota_enable_per_user_proxy_read === '1') {
    //                 userQuotaName = _getQuotaName(r, USER, userId, API_READ);
    //             }
    //             break;
    //         case 'POST':
    //         case 'PUT':
    //         case 'DELETE':
    //             if (r.variables.quota_enable_per_user_proxy_write &&
    //                 r.variables.quota_enable_per_user_proxy_write === '1') {
    //                 userQuotaName = _getQuotaName(r, USER, userId, API_WRITE);
    //             }
    //     }
    //     }
    // // Set keys of key-val zone to check quota-remaining
    // if (userQuotaName !== '') {
    //     r.variables.user_quota_name = userQuotaName;
    //     r.variables.user_id_quota_name = userId + ':' + userQuotaName;
    //     r.log('validating quota-remaining: ' + r.variables.user_id_quota_name);
    // }

    // // Validate if quota remains on a user and proxy
    // let now = r.variables.time_local;
    // let msgPrefix = '[quota : ' + userQuotaName + '] ';
    // if (!r.variables.user_quota_remaining) {
    //     r.error(msgPrefix + 'not found')
    //     r.return(401);
    // } else if (r.variables.quota_remaining > 0) {
    //     if (r.variables.user_quota_expiry_time > now) {
    //         r.error(msgPrefix + 'expired');
    //         // TODO: reset quota limit with new start time unless quota is disabled.
    //         _setHeadersOut(r, now);
    //         r.return(403);
    //         return;
    //     }
    //     r.return(204);
    // } else {
    //     r.error(msgPrefix + 'exhausted');
    //     _setHeadersOut(r, now);
    //     r.return(403);
    // }
}

// Quota Limiting Request: Group or User Level Quota Decrement
//
function decreaseQuota(r) {
    r.log('quota decrement for ' + r.variables.user_id_quota_name);
    
    // TODO: stand-alone quota decrement
    if (r.variables.user_quota_remaining) {
        r.variables.user_quota_remaining--;
        r.variables.user_quota_last_update = Date().getTime();
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
    r.headersOut['X-User-Quota-Policy'] = r.variables.user_id_quota_name;
    r.headersOut['X-User-Quota-Limit'] = r.variables.user_quota_limit;
    r.headersOut['X-User-Quota-Remaining'] = r.variables.user_quota_remaining;
    r.headersOut['X-User-Quota-Reset'] = r.variables.user_quota_expiry_time - now;
    // r.headersOut['X-Group-Quota-Limit'] = r.variables.group_quota_limit;
    // r.headersOut['X-Group-Quota-Remaining'] = r.variables.group_quota_remaining;
}

/**
 * Get quota name
 *
 * @param r {Request} HTTP request object
 * @param quotaType {string} quota type
 * @param consumerId {string} user-id, group-id, or global-id
 * @param apiMethod {string} api-method
 * @returns {string} quota payment method
 * @private
 */
function _getQuotaName(r, quotaType, consumerId, apiMethod) {
    let userQuotaName = '';
    const proxyNameMethod = r.variables.proxy_name + ':' + apiMethod;
    const consumerProxyMethod = consumerId + ':' + proxyNameMethod;
    const quotaTypeProxyNameMethod = quotaType + ':' + proxyNameMethod;

    r.variables.user_proxy_method = consumerProxyMethod;
    if (r.variables.quota_payment_method) {
        userQuotaName = quotaTypeProxyNameMethod + ':' + r.variables.quota_payment_method;
    }
    // if (consumerProxyMethod in r.variables.user_proxy_method) {
    //     r.variables.user_proxy_method = consumerProxyMethod;
    //     userQuotaName = quotaTypeProxyNameMethod + ':' + r.variables.quota_payment_method;
    // }
    // TODO: Get group/global quota name
    return userQuotaName;
}

/**
 * Get quota zone name
 *
 * @param r {Request} HTTP request object
 * @param consumerType {string} consumer type: USR, or CLN for client.ID
 * @param isQuotaRemaining {boolean} option to generate zone name for quota-remaining
 * @returns {string} quota zone name to find key/val from key/val store
 * @private
 */
function _getZoneName(r, consumerType, isQuotaRemaining) {
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
    const quotaDataType = isQuotaRemaining ? 'remaining_' : 'meta_data_';
    const zoneName = consumerType.concat(
        '_quota_', quotaDataType,
        r.variables.proxy_name, '_',
        r.variables.proxy_ver, '_', 
        readWrite
    );
    return zoneName
}

export default {
    decreaseQuota,
    setUserQuotaLimit,
    validateQuota
}
