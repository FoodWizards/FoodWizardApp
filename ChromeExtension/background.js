const CLIENT_ID = encodeURIComponent('669601198231-9nlmatmmdkiasqrnl2mgvufhahfoh7no.apps.googleusercontent.com');
const RESPONSE_TYPE = encodeURIComponent('id_token');
const REDIRECT_URI = encodeURIComponent('https://jbimcanopnhpajhgmnippneolodejkeg.chromiumapp.org/')
const SCOPE = encodeURIComponent('openid email profile');
const STATE = encodeURIComponent('meet' + Math.random().toString(36).substring(2, 15));
const PROMPT = encodeURIComponent('consent');

let user_signed_in = false;

function is_user_signed_in() {
    return user_signed_in;
}

function create_auth_endpoint() {
    let nonce = encodeURIComponent(Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15));

    let openId_endpoint_url =
        `https://accounts.google.com/o/oauth2/v2/auth
?client_id=${CLIENT_ID}
&response_type=${RESPONSE_TYPE}
&redirect_uri=${REDIRECT_URI}
&scope=${SCOPE}
&state=${STATE}
&nonce=${nonce}
&prompt=${PROMPT}`;

    console.log(openId_endpoint_url);
    return openId_endpoint_url;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === 'login') {
        if (user_signed_in) {
            console.log("User is already signed in.");
        } else {
            chrome.identity.launchWebAuthFlow({
                'url': create_auth_endpoint(),
                'interactive': true
            }, function (redirect_url) {
                if (chrome.runtime.lastError) {
                    // problem signing in
                } else {
                    let id_token = redirect_url.substring(redirect_url.indexOf('id_token=') + 9);
                    id_token = id_token.substring(0, id_token.indexOf('&'));
                    const payload = JSON.parse(atob(id_token.split('.')[1]));
                
                    if (payload.iss === 'https://accounts.google.com' && payload.aud === CLIENT_ID){
                        console.log("User successfully signed in.");
                        user_signed_in = true;
                        chrome.storage.local.set({ foodWizard_token: id_token });
                        console.log('outside storage get token')
                        chrome.storage.local.get('foodWizard_token', (data)=> {
                            console.log('inside storage get token')
                            console.log(data.foodWizard_token)
                        })


                        chrome.action.setPopup({ popup: './popup-signed-in.html' }, () => {
                            sendResponse('success');
                        });



                    } else {
                        // invalid credentials
                        console.log("Invalid credentials.");
                    }
                }
            });

            return true;
        }
    }
    else if (request.message === 'logout') {
        user_signed_in = false;
        chrome.action.setPopup({ popup: './popup.html' }, () => {
            sendResponse('success');
        });

        return true;
    } else if (request.message === 'isUserSignedIn') {
        sendResponse(is_user_signed_in());
    }
});


//exports.sendDataToServer = {sendDataToServer };