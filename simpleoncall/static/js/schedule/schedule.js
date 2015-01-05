var addNewSchedule = function(){
    var newSchedule = document.querySelector('#new-schedule-form section').cloneNode(true);
    var editSchedule = document.querySelector('#edit-schedule');
    editSchedule.appendChild(newSchedule);
};

document.addEventListener('DOMContentLoaded', function(){
    var editSchedule = document.querySelector('#edit-schedule');
    editSchedule.addEventListener('click', function(e){
        if(e.target.classList.contains('add-new-schedule')){
            addNewSchedule();
        }
    });
});
