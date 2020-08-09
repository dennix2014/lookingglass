$('#form').on('submit', function(e){
    e.preventDefault();
    $('.wrap-every').hide();
    $('.loading').css("display", "block")

    $.ajax({
       type : "POST", 
       url: $(this).attr('action'),
       data: {
        ip_address : $('#ip_address').val(),
        command: $('#command').find(":selected").val(),
        csrfmiddlewaretoken: $("form").find('input[name=csrfmiddlewaretoken]').val(),
        dataType: "json",

       },

       success: function(data){
        $('.loading').hide();
        $('.return-home').css("display", "block")
        $('#output').html(data.result)/* response message */
       },

       error: function(XMLHttpRequest, textStatus, errorThrown) { 
           $('.loading').hide();
           $('#output').html(`<p class="text-danger text-center">${errorThrown}</p>`)
    
            }      
    });
});     
