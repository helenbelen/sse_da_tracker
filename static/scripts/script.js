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
	console.log("List Change:");
	console.log("Cookie " + this.getCookie("list"));
	console.log("List: ")
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


function new_page(button_name) {
	if (this.getCookie("list").length > 0){
		this.setCookie("list", this.getCookie("list") + selected_list);
	}
	else{
		this.setCookie("list",selected_list);
	}
	console.log("New Page");
	console.log(this.getCookie("list"));
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	    if (this.readyState == 4 && this.status == 200) {
	    	window.location.reload();
	    	console.log("Page Loaded");

	    }
	  };
	xhttp.open("POST", "/page", true);
	xhttp.setRequestHeader("Content-type", "application/json;;charset=UTF-8");
	data = JSON.stringify({data : button_name});
	xhttp.send(data);

}


function setCookie(cname,array_list) {
	
    document.cookie = cname + "=" + array_list +";";
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}