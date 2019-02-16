function get(endpoint, cb){
    var request = new XMLHttpRequest();
    request.open('GET', endpoint, true);
    request.onreadystatechange = function (){
        if (request.readyState === XMLHttpRequest.DONE && request.status === 200){
            try {
                var data = JSON.parse(request.response);  // normally json data but captcha is in bytes
            }
            catch {
                var data = request.response;
            }
            cb(data);
        }
    };
    request.send();
}