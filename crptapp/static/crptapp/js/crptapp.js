function setFocusFirstElemForm(){
  if(document.forms){
    form = document.forms[0];
    if(form){
       if(form.elements){
          form.elements[0].focus();
       }
    }
  }
}


function toggleClassElements(name){
   var elements = document.getElementsByClassName(name);
   var section_display = "";

   for (var i = 0; i < elements.length; ++i) {
      var element = elements[i];
      // Control section display. If it is "none" all children must be hidden
      if(section_display=="none"){
         element.style.display="none";
         continue;
      }
      // Toggle display
      if (element.style.display!="none"){
         element.style.display="none"
      }else{
         element.style.display=""
      }
      // Save control section display status. Convention className==name
      if(element.className==name){
         section_display = element.style.display;
      }
      if(i==elements.length){
        return;
      }
   }
}

function enableDisabledSelects(){
   elements = document.getElementsByTagName('select');
   for (var i = 0; i < elements.length; ++i) {
      if (elements[i].disabled==true) {
         elements[i].disabled = false;
      }
   }
}