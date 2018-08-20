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