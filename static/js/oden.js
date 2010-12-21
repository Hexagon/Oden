/* #seach_submit.click */
$(function() {  
 $('body').click(function(event) {

   /* #search_submit.click */
   if ($(event.target).is('#search_submit')) {
    var q = 'q=' + $("input#search_q").val();
    $.ajax({
      type: "POST",
      url: "/ajax/person_by_handle",
      data: q,
      success: function(msg){
        $("#search_result").append(msg);
      },
      error: function(msg,error){
        alert('Could not find this person');
      },
      timeout: function(msg){
        alert('Timeout ocurred while searching for person');
      }
    });
   }

   /* #add_person.click */
   if ($(event.target).is("#add_contact")) {
    var id = 'id=' + $("input#contact_guid").val() + '&aspect=' + $("input#aspect_guid").val();
    $.ajax({
      type: "POST",
      url: "/ajax/add_contact",
      data: id,
      success: function(msg){
        alert('Request sent to person');
      },
      error: function(msg,error){
        alert('Could not add this person');
      },
      timeout: function(msg){
        alert('Timeout ocurred while adding person');
      }
    });
   }
 }); 
});

