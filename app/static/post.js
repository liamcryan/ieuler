function post(endpoint, data, cb){
    var request = new XMLHttpRequest();
    request.open('POST', endpoint, true);
    // request.setRequestHeader('Content-type', 'application/json');
    request.onreadystatechange = function () {
        if (request.readyState === XMLHttpRequest.DONE && request.status === 200){
            var data = JSON.parse(request.response);
            cb(data);
        }
    };
    request.send(data);
}