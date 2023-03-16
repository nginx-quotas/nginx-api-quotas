/**
 * Distributed Quota Limiter Client with NGINX
 */

export default {
    decrement
}


// Quota Limiting Request: Group or User Level Quota Decrement
//
function decrement(r) {
    var uri = '/quotas/decrement/';
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
