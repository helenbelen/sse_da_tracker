var selected_list = []

function select_all(){
	checkboxes = document.getElementsByName("video");
	for(i = 0; i < checkboxes.length; i++){
		if (document.getElementById("SelectAll").checked == true){
			checkboxes[i].checked = true;
		}
		else{
			checkboxes[i].checked = false;
		}
		list_edit(checkboxes[i],checkboxes[i].value);
	}
}

function list_edit(check, value){
	console.log(value)
	if(check.checked == false && selected_list.indexOf(value) >= 0){
		//remove item
		selected_list.splice(selected_list.indexOf(value),selected_list.indexOf(value)+1);
	}
	else if (check.checked == true && selected_list.indexOf(value) < 0){
		// add item
		selected_list.push(value)
	}
	
	console.log(selected_list)
}

function send_selected() {
if(selected_list.length > 0){
	  
	  var xhttp = new XMLHttpRequest();
	  xhttp.onreadystatechange = function() {
	    if (this.readyState == 4 && this.status == 200) {
	    	var date = new Date();
	     	var element = document.createElement('a');
	     	element.setAttribute('href','data:text/csv;charset=utf-8,' + xhttp.responseText);
	     	element.setAttribute('download','DAReport-' + date.toDateString());
	     	element.style.display = 'none'
	     	document.body.appendChild(element);
	     	element.click();
	     	document.body.removeChild(element);

	    }
	  };
	  xhttp.open("POST", "/download-file", true);
	  xhttp.setRequestHeader("Content-type", "application/json;;charset=UTF-8");
	  data = JSON.stringify({data : selected_list});
	  xhttp.send(data);
 }
 else{
 	alert("Please Select At Least One Video To Download To A File.")
 }
}


