/**
 * JavaScript functions for testing NGINX API Quota Management
 * 
 * Copyright (C) 2023 Nginx, Inc.
 */

// Constants for common error message.
var isSignedIn = false;
var TITLE_SIGNIN = 'Sign in';
var TITLE_SIGNOUT = 'Sign out';
var MSG_SIGNINIG_IN = 'Signinig in';
var MSG_SIGNED_IN = 'Signed in';
var MSG_SIGNED_OUT = 'Signed out';
var MSG_EMPTY_JSON = '{"message": "N/A"}';
var MSG_DELETED_JSON = '{"message": "Deleted"}';
var MSG_NOTFOUND_JSON = '{"message": "Not found or already deleted"}';
var MSG_TOOMANYREQ_JSON = '{"message": "Too many requests"}';
var MSG_DELETED = 'Deleted'
var MSG_NOTFOUND = 'Not found or already deleted'
var MSG_TOOMANYREQ = 'Too many requests';
var btnSignin = document.getElementById('signin');
var btnPutCfgGlobal = document.getElementById('put-global-limit');
var btnDelCfgGlobal = document.getElementById('del-global-limit');
var btnPutCfgUser = document.getElementById('put-user-limit');
var btnDelCfgUser = document.getElementById('del-user-limit');
var btnUploadImg = document.getElementById('upload-image');
var btnDnloadImg = document.getElementById('download-image');
var txtGlobalQuotaLimit = document.getElementById('global-quota-limit')
var txtUserQuotaLimit = document.getElementById('user-quota-limit')
var jsonViewer = new JSONViewer();
var viewerJSON = document.querySelector("#json").appendChild(jsonViewer.getContainer());
var userName = '';
var userId = '';


/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                             *
 *                        0. Initialize Main Page                              *
 *                                                                             *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
var initButtons = function () {
  if (isSignedIn) {
    initButtonsAfterSignIn()
  } else {
    initButtonsBeforeSignIn()
  }
}


var initButtonsBeforeSignIn = function () {
  btnPutCfgUser.disabled = true
  btnDelCfgUser.disabled = true
  isSignedIn = false;
  userId = '';
  showLoginBtnTitle(TITLE_SIGNIN);
}

var initButtonsAfterSignIn = function () {
  btnPutCfgUser.disabled = false
  btnDelCfgUser.disabled = false
  isSignedIn = true;
  showLoginBtnTitle(TITLE_SIGNOUT);
}

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                             *
 *              1. Event Handler for testing NGINX Quota Management            *
 *                                                                             *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

// Event Handler: for when clicking a either 'Sign in' or `Sign out` button.
var eventHandlerSignIn = function (evt) {
  if (!isSignedIn) {
    doSignIn(evt)
  } else {
    doSignOut(evt)
  }
};

// Event Handler: for when clicking a button 'Configure a global rate limiter'.
var eventHandlerPutCfgGlobal = function (evt) {
  var headers = { 'Content-Type': 'application/json' };
  var body = {
    'quota_limit': getGlobalQuotaLimit(),
    'limit_per': 'rps'
  };
  doAPIRequest(
    evt,
    '/ratelimits/config/global',
    'PUT',
    'configuring a global rate limit...',
    'configured a global rate limit',
    headers,
    JSON.stringify(body)
  )
};

// Event Handler: for when clicking a button 'Delete a global rate limiter'.
var eventHandlerDelCfgGlobal = function (evt) {
  var headers = { 'Content-Type': 'application/json' };
  var body = {
    'quota_limit': getGlobalQuotaLimit(),
    'limit_per': 'rps'
  };
  doAPIRequest(
    evt,
    '/ratelimits/config/global',
    'DELETE',
    'deleting a global rate limit...',
    'deleted a global rate limit',
    headers,
    JSON.stringify(body)
  )
};

// Event Handler: for when clicking a button 'Configure a user rate limiter'.
var eventHandlerPutCfgUser = function (evt) {
  var headers = { 'Content-Type': 'application/json' };
  var uri = '/ratelimits/config/users/' + userId;
  var body = {
    'quota_limit': getUserQuotaLimit(),
    'limit_per': 'rps'
  };
  doAPIRequest(
    evt,
    uri,
    'PUT',
    'configuring a user rate limit...',
    'configured a user rate limit',
    headers,
    JSON.stringify(body)
  )
};

// Event Handler: for when clicking a button 'Delete a user rate limiter'.
var eventHandlerDelCfgUser = function (evt) {
  var headers = {
    'Content-Type': 'application/json'
  };
  var uri = '/ratelimits/config/users/' + userId;
  var body = {
    'quota_limit': getUserQuotaLimit(),
    'limit_per': 'rps'
  };
  doAPIRequest(
    evt,
    uri,
    'DELETE',
    'deleting a user rate limit...',
    'deleted a user rate limit',
    headers,
    JSON.stringify(body)
  )
};


// Event Handler: for when clicking a button 'Upload an image file'.
var eventHandlerUploadImg = function (evt) {
  var headers = {
    'Content-Type': 'application/json', 'Cookie': 'user_id=' + userId
  };
  var uri = '/images';
  var body = null;
  setCookie('user_id', userId)
  doAPIRequest(
    evt,
    uri,
    'GET',
    'uploading an image...',
    'uploaded an image',
    headers,
    body
  )
};

// Event Handler: for when clicking a button 'Download an image file'.
var eventHandlerDnloadImg = function (evt) {
  var headers = { 'Content-Type': 'application/json' };
  var uri = '/dummy';
  var body = null;
  doAPIRequest(
    evt,
    uri,
    'GET',
    'requesting dummy API...',
    'requested dummy API.',
    headers,
    body
  )
};

// Event Handler: for when clicking a 'Get User Info' button.
var eventHandlerUserInfo = function (evt) {
  showUserInfo(evt)
};


/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                             *
 *       2. Common Functions for testing NGINX Quota Mgmt. via Sample UI       *
 *                                                                             *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

// Request NGINX endpoint which is a location block.
var doNginxEndpointRequest = function (evt, uri) {
  if (evt && evt.type === 'keypress' && evt.keyCode !== 13) {
    return;
  }
  location.href = window.location.origin + uri;
};

var eraseCookie = function (name) {
  document.cookie = name + '=; Path=/; SameSite=lax;';
}

var setCookie = function (name, value) {
  document.cookie = name + '=' + value + '; Path=/; SameSite=lax;';
}

// Sign in by clicking 'Sign In' button of the UI.
var doSignIn = function (evt) {
  eraseCookie('session_id')
  eraseCookie('auth_redir')
  eraseCookie('auth_nonce')

  doNginxEndpointRequest(evt, '/login');
};

// Sign in by clicking 'Sign In' button of the UI.
var doSignOut = function (evt) {
  doNginxEndpointRequest(evt, '/logout');
};

// Request an API with application/json type response.
var doAPIRequest = function (
  evt, uri, method, msgBefore, msgAfter, headers, body
) {
  if (evt && evt.type === 'keypress' && evt.keyCode !== 13) {
    return false;
  }
  showMessage(msgBefore)
  const url = window.location.origin + uri;
  var status = 200;
  fetch(url, {
    method: method,
    mode: 'cors',
    headers: headers,
    body: body
  })
    .then((response) => {
      showResponseStatus(response.status, response.statusText, url)
      showMessageDetail(MSG_EMPTY_JSON)
      status = response.status;
      if (response.ok || response.status == 400) {
        showMessage(msgAfter)
        return response.json();
      } else if (response.status == 204) {
        showMessage(msgAfter)
        return MSG_DELETED_JSON;
      } else if (response.status == 404) {
        showMessage(MSG_NOTFOUND)
        return MSG_NOTFOUND_JSON;
      } else if (response.status == 429) {
        showMessage(MSG_TOOMANYREQ)
        return MSG_TOOMANYREQ_JSON;
      }
      throw new Error(response.error)
    })
    .then((data) => {
      if (status != 204) {
        showMessageDetail(JSON.stringify(data))
      }
      if (uri == '/userinfo') {
        initButtonsAfterSignIn()
        if (data.username) {
          userName = data.username;
          showMessage(userName)
        } else if (data.name) {
          userName = data.name;
          showMessage(userName)
        } else if (data.email) {
          userName = data.email;
          showMessage(userName)
        }
        if (data.sub) {
          userId = data.sub;
        }
      }
    })
    .catch(function (error) {
      if (uri == '/userinfo') {
        initButtonsBeforeSignIn()
        showMessage('Need to sign-in to retrieve user info!');
        showMessageDetail(MSG_EMPTY_JSON)
      } else {
        if (status != 204) {
          showMessage(error);
          showMessageDetail(MSG_EMPTY_JSON)
        } else {
          showMessage(MSG_DELETED);
          showMessageDetail(MSG_DELETED_JSON)
        }

      }
    });
  return true;
}

// Show user information in the UI via the endpoint of /userinfo
var showUserInfo = function (evt) {
  var headers = {};
  doAPIRequest(
    evt,
    '/userinfo',
    'GET',
    'getting user info from IdP...',
    'user info: received from IdP',
    headers,
    null
  );
}

// Display summarized message for each testing.
var showMessage = function (msg) {
  document.getElementById('message').value = msg;
};

// Display response status & message for each testing.
var showResponseStatus = function (status, msg, uri) {
  document.querySelector('pre').textContent = uri + ', ' + status + ', ' + msg;
};

// Clear message window
var clearMessage = function () {
  document.querySelector('pre').textContent = '';
  showMessageDetail(MSG_EMPTY_JSON);
};

// Display detail message for each testing.
var showMessageDetail = function (msg) {
  var setJSON = function () {
    try {
      jsonObj = JSON.parse(msg);
    }
    catch (err) {
      alert(err);
    }
  };
  setJSON();
  jsonViewer.showJSON(jsonObj);
  var res = jsonObj;
  return res
}

// Display a button title for toggling between 'Sign in' and 'Sign out'.
var showLoginBtnTitle = function (msg) {
  btnSignin.innerText = msg
};

// Display 'Sign In' button when signed-out or occurs error during signing-in.
var showSignInBtn = function () {
  isSignedIn = false;
  showLoginBtnTitle(TITLE_SIGNIN);
  showMessage(MSG_SIGNED_OUT);
};

// Display 'Sign Out' button when signed-in.
var showSignOutBtn = function () {
  isSignedIn = true;
  showLoginBtnTitle(TITLE_SIGNOUT);
  showMessage(MSG_SIGNED_IN);
};

var getGlobalQuotaLimit = function () {
  return txtGlobalQuotaLimit.value;
};

var getUserQuotaLimit = function () {
  return txtUserQuotaLimit.value;
};

var getAPIReqCnt = function () {
  return txtAPIReqCnt.value;
};

// Return cookie value using key
var getCookieValue = function (key) {
  var cookies = document.cookie;
  var parts = cookies.split(key + "=");
  var cookieValue = '';
  if (parts.length == 2) {
    cookieValue = parts.pop().split(";").shift();
  }
  return cookieValue;
}


// Add event lister of each button for testing NGINX Plus OIDC integration.
btnSignin.addEventListener('click', eventHandlerSignIn);
btnPutCfgGlobal.addEventListener('click', eventHandlerPutCfgGlobal);
btnDelCfgGlobal.addEventListener('click', eventHandlerDelCfgGlobal);
btnPutCfgUser.addEventListener('click', eventHandlerPutCfgUser);
btnDelCfgUser.addEventListener('click', eventHandlerDelCfgUser);
btnUploadImg.addEventListener('click', eventHandlerUploadImg);
btnDnloadImg.addEventListener('click', eventHandlerDnloadImg);

showUserInfo(null)
