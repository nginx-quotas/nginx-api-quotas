
function testEachMonth() {
    const now = new Date();
    const lNow = now.getTime();
    const lAfter1h = _getExpiryTime(lNow, REQ_HOUR);
    const after1h = new Date(lAfter1h);
    let after1M = new Date(now.getFullYear(), now.getMonth() + 1, now.getDate()+8);
    let lAfter1M = after1M.getTime();
    r.log("now       : ".concat(now, '(', lNow, ')'));
    r.log("next hour : ".concat(after1h, '(', lAfter1h, ')'));
    r.log("next month: ".concat(after1M, '(', lAfter1M, ')'));

    for (var m = 0; m <= 11; m++) {
        lAfter1M = _getExpiryTime(lAfter1M, REQ_MON);
        after1M = new Date(lAfter1M);
        r.log("next month: ".concat(after1M, '(', lAfter1M, ')'));
    }
}