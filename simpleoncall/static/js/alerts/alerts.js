document.addEventListener('DOMContentLoaded', function(){
    var alerts = document.querySelector('#alerts');
    alerts.addEventListener('click', function(e){
        var parent = e.target.parentElement;
        if(parent.classList.contains('header')){
            var details = parent.parentElement.querySelector('.details');
            if(details.classList.contains('hidden')){
                details.classList.remove('hidden');
            } else {
                details.classList.add('hidden');
            }
        }
    });
});
