var SimpleOnCall = (function($){
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

    $.fn.value = function(value){
        this.forEach(function(elm){
            if(elm.hasOwnProperty('value')){
                elm.value = value;
            }
        }.bind(this));
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

    simpleoncall.sendFormData = function(form, data, handler){
        if(typeof data === 'function'){
            handler = data;
            data = {};
        }
        if(typeof handler !== 'function'){
            handler = function(err, request){
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
                form.dispatchEvent(newEvent);
            };
        }
        $.ajax({
            url: form.action,
            method: form.method,
            data: JSON.stringify(data),
            headers: {
                'X-CSRFToken': data.csrfmiddlewaretoken,
            },
            dataType: 'application/json',
            responseType: 'json',
        }, handler);
    };

    $.on('submit', 'form[data-ajax-submit]', function(evt){
        evt.preventDefault();
        var form = evt.target;
        var data = $(form).serialize();
        simpleoncall.sendFormData(form, data);
    });

    $.on('form-response', 'form[data-ajax-response]', function(evt){
        if(evt.detail && evt.detail.html){
            var id = '#' + evt.target.dataset.ajaxResponse;
            $(id)[0].innerHTML = evt.detail.html;
        }
    });

    return simpleoncall;
})(window.Scant);


var getAlertSettings = function(){
    return $('#alert-schedule form .alert-setting-row').map(function(elm){
        var $elm = $(elm);
        return {
            id: parseInt(elm.dataset.id),
            type: $elm.find('[name=alert_type]')[0].value,
            time: $elm.find('[name=alert_time]')[0].value,
        }
    });
};

$('#alert-schedule').on('submit', 'form', function(evt){
    evt.preventDefault();
    evt.stopPropagation();

    var data = {
        'csrfmiddlewaretoken': $(evt.target).find('[name=csrfmiddlewaretoken]')[0].value,
        'settings': getAlertSettings(),
    };

    SimpleOnCall.sendFormData(evt.target, data);
});

$.on('click', '#add-alert-row .icon', function(evt){
    var existing = document.querySelector('.alert-setting-row.disabled');
    if(existing){
        var newRow = existing.cloneNode(true);
        newRow.className = 'alert-setting-row';
        newRow.dataset.id = 0;
        var addAlert = document.getElementById('add-alert-row');
        var alertForm = document.getElementById('alert-settings-form');
        alertForm.insertBefore(newRow, addAlert);
    }
});

$.on('click', '.remove-alert-row .icon', function(evt){
    evt.target.parentElement.parentElement.remove();
});

$.on('click', '#api-key-create', function(evt){
    evt.preventDefault();
    evt.stopPropagation();
    $.ajax({
        url: evt.target.href,
        responseType: 'json',
    }, function(err, request){
        if(!err && request.response && request.response.html){
            $('#api-keys')[0].innerHTML = request.response.html;
        }
    });
});
