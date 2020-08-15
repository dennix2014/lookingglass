$('#form').on('submit', function(e){
    e.preventDefault();
    $('.loading').css("display", "block");
    $('#output').hide();
    $('.btn').prop("disabled",true);

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
        $('#output').show();
        $('#output').html(data.result)
        $('.btn').prop("disabled",false);
       },
       

       error: function(XMLHttpRequest, textStatus, errorThrown) { 
           $('.loading').hide();
           $('#output').show();
           $('#output').html(`<p class="text-danger text-center">${errorThrown}</p>`)
    
            }      
    });
});     

$('.return-home').on('click', function(e){
    e.preventDefault();
    $('.return-home').hide()
    $('.wrap-every').show();
    $('#output').hide();

});     
