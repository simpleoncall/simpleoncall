(function($){
    var simpleoncall = {};

    simpleoncall.fetchPartial = function(partial, callback){
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

    $.fn.fetchPartial = function(name, callback){
        if(typeof callback !== 'function'){
            callback = function(){};
        }
        simpleoncall.fetchPartial(name, function(err, html){
            if(err || !html){
                return callback(false);
            }

            this.forEach(function(elm){
                elm.innerHTML = html;
            }.bind(this));

            callback(true);
        }.bind(this));
    };

    simpleoncall.formHandler = function(evt){
        evt.preventDefault();
        var form = evt.target;
        var data = $(form).serialize();
        $.ajax({
            url: form.action,
            method: form.method,
            data: JSON.stringify(data),
            headers: {
                'X-CSRFToken': data.csrfmiddlewaretoken,
            },
            dataType: 'application/json',
            responseType: 'json',
        }, function(err, request){
            var response = request.response || {};
            if(response && response.redirect){
                window.location = response.redirect;
                return;
            }
            var newEvent = new CustomEvent('form-response', {
                detail: {
                    error: err || response.error || true,
                    html: response.html || null,
                },
                bubbles: true,
                cancelable: true,
            });
            evt.target.dispatchEvent(newEvent);
        });
    };
    $.on('submit', 'form', SimpleOnCall.formHandler);

    $.on('form-response', '#login form', function(evt){
        if(evt.detail && evt.detail.html){
            $('#login')[0].innerHTML = evt.detail.html;
        }
    });

    $.on('form-response', '#register form', function(evt){
        if(evt.detail && evt.detail.html){
            $('#register')[0].innerHTML = evt.detail.html;
        }
    });

})(window.Scant);
