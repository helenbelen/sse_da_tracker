


function select_all(){
	checkboxes = document.getElementsByName("video");
	for(i = 0; i < checkboxes.length; i++){
		if (document.getElementById("SelectAll").checked == true){
			checkboxes[i].checked = true;
		}
		else{
			checkboxes[i].checked = false;
		}
		save_check(checkboxes[i],checkboxes[i].value);
	}
}


function send_selected() {
	my_list = get_selected();
	console.log("Selected:")
	console.log(my_list);
	if(my_list.length > 0){
		get_selected();
		var xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
	    if (this.readyState == 4 && this.status == 200) {
	    	var date = new Date();
	     	var element = document.createElement('a');
	     	element.setAttribute('href','data:text/csv;charset=utf-8,' + xhttp.responseText);
	     	element.setAttribute('download','DAReport-' + date.toDateString() + '.csv');
	     	element.style.display = 'none'
	     	document.body.appendChild(element);
	     	element.click();
	     	document.body.removeChild(element);
	     	sessionStorage.clear();
	     	reset_checks();
	    }
	  };
	  xhttp.open("POST", "/download-file", true);
	  xhttp.setRequestHeader("Content-type", "application/json;;charset=UTF-8");
	  data = JSON.stringify({data : my_list});
	  xhttp.send(data);
 	}
 	else{
 		alert("Please Select At Least One Video To Download To A File.")
 	}
}

function get_selected(){
	my_list = [];
	for(i=0;i < sessionStorage.length;i++){
		my_list.push(sessionStorage.key(i));
	}

	console.log("My List");
	console.log(my_list);
	return my_list;
}

function new_page(button_name) {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	    if (this.readyState == 4 && this.status == 200) {
	    	window.location.reload();
	    	console.log("Page Loaded");


	    }
	  };
	xhttp.open("POST", "/page", true);
	xhttp.setRequestHeader("Content-type", "application/json;;charset=UTF-8");
	
	data = JSON.stringify({data : button_name, selected : sessionStorage});
	console.log(data);
	xhttp.send(data);

}

function storage_available(){
	if (typeof(Storage) == "undefined"){
		console.log("This app will not work. Storage undefined");
		alert("This app will not work. Storage undefined");
		return false;
	}
	else{
		return true;
	}
}

function save_check(check = null, value = null){
	if(storage_available()){
		if (value == null){
			checkboxes = document.getElementsByName("video");
			for(i = 0; i < checkboxes.length; i++){
				storage_update(checkboxes[i],checkboxes[i].value);
			}
		}
		else{
			storage_update(check,value);
		}
		console.log(sessionStorage)
	}
}


function storage_update(check,value){
	if(sessionStorage.getItem(value) != null && check.checked == false){
		sessionStorage.removeItem(value);
	}
	else if (sessionStorage.getItem(value) == null && check.checked == true) {
		sessionStorage.setItem(value,"selected");

	}
}

function reset_checks(){
	checkboxes = document.getElementsByName("video");
	for(i = 0; i < checkboxes.length; i++){
		if(sessionStorage.getItem(checkboxes[i].value) != null){
			checkboxes[i].checked = true;
		}
	}

	
}
