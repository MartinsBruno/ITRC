var availabilitySelect = document.getElementById("availabilityHostgroup");
var triggerSelect = document.getElementById("triggerSelect");
availabilitySelect.onchange = function(){
    var hostgroupid = availabilitySelect.value;
    fetch("/js-request/triggers-by-hostgroup/" + hostgroupid).then(function(response){
        response.json().then(function(data) {
            var optionHTML = '';
            for (var trigger of data.triggers) {
                optionHTML += '<option value="' + trigger.description + '">' + trigger.description + '</option>';
            } triggerSelect.innerHTML = optionHTML
        });
    });
};