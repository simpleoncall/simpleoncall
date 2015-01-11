var soc = window.soc || {};

soc.fetchPartial = function(partial, callback){
    $.ajax({
        url: '/partial/' + partial,
        responseType: 'json',
    }, function(err, result){
        if(err === null && result.response && result.response.html){
            callback(null, result.response.html);
        } else {
            callback(true, null);
        }
    });
};
