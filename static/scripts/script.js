var selected_list = []

function select_all(){
	if (document.getElementById("SelectAll").checked == true){
		checkboxes = document.getElementsByName("video");
		for(i = 0; i < checkboxes.length; i++){
			checkboxes[i].checked = true;
		}
	}
	else{
		for(i = 0; i < checkboxes.length; i++){
			checkboxes[i].checked = false;
		}
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
	console.log(selected_list)
  var xhttp = new XMLHttpRequest();
  // xhttp.onreadystatechange = function() {
  //   if (this.readyState == 4 && this.status == 200) {
      
  //   }
  // };
  xhttp.open("POST", "/download-file", true);
  xhttp.setRequestHeader("Content-type", "application/json;;charset=UTF-8");
  data = JSON.stringify({data : selected_list});
  xhttp.send(data);
}


