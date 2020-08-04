$('#form').on('submit', function(e){
    e.preventDefault();
    $('#form').hide();
    $('.load').show();

$.ajax({
   type : "POST",
   url: $(this).attr('action'),
   data: {
    ip_address : $('#ip_address').val(),
    command : $("input[name='command']:checked").val(),
    csrfmiddlewaretoken: $("#form").find('input[name=csrfmiddlewaretoken]').val(),
    dataType: "json",

   },
   
   success: function(data){
    $('.load').hide();
    $('#output').html(data.result) /* response message */
   },

   error: function(XMLHttpRequest, textStatus, errorThrown) { 
       $('.load').hide();
       $('#output').html(`<p class="text-danger text-center">${errorThrown}</p>`)
    
}      


});


    });     
