function scrollToElement(id_or_class){
    $('html, body').animate({
        scrollTop: $(id_or_class).offset().top
    }, 1000);
}

$(document).ready(function() {
    $("#command, #server").on('load change', function() {
        var selected_command = $('#command').val();
        var selected_server = $('#server').val();
        if (selected_command == 'bgp_neighbors') {
            $('#ip_add').hide();
            $('#los_nei').hide();
            $('#abj_nei').hide();
            $('#los_nei_v6').hide();
            $('#ip_address').removeAttr('required');
            $('#ip_address').removeAttr('data-error');
            $('#los_neighbors').removeAttr('required');
            $('#los_neighbors').removeAttr('data-error');
            $('#abj_neighbors').removeAttr('required');
            $('#abj_neighbors').removeAttr('data-error');
            $('#los_neighbors_v6').removeAttr('required');
            $('#los_neighbors_v6').removeAttr('data-error');
        } else if (selected_command == 'bgp_neighbor_received' && selected_server == "rs3.abj.v4"){
            scrollToElement(".submit-button");
            $('#ip_add').hide();
            $('#los_nei').hide();
            $('#los_nei_v6').hide();
            $('#ip_address').removeAttr('required');
            $('#ip_address').removeAttr('data-error');
            $('#los_neighbors').removeAttr('required');
            $('#los_neighbors').removeAttr('data-error');
            $('#los_neighbors_v6').removeAttr('required');
            $('#los_neighbors_v6').removeAttr('data-error');
            $('#abj_nei').show();
            $('#abj_neighbors').attr('required', '');
            $('#abj_neighbors').attr('data-error', 'This field is required');

        }else if (selected_command == 'bgp_neighbor_received' && (selected_server == "rs1.rc.v4" || selected_server == "rs2.med.v4") ){
            scrollToElement(".submit-button");
            $('#ip_add').hide();
            $('#abj_nei').hide();
            $('#los_nei_v6').hide();
            $('#ip_address').removeAttr('required');
            $('#ip_address').removeAttr('data-error');
            $('#abj_neighbors').removeAttr('required');
            $('#abj_neighbors').removeAttr('data-error');
            $('#los_neighbors_v6').removeAttr('required');
            $('#los_neighbors_v6').removeAttr('data-error');
            $('#los_nei').show();
            $('#los_neighbors').attr('required', '');
            $('#los_neighbors').attr('data-error', 'This field is required');

        }else if (selected_command == 'bgp_neighbor_received' && selected_server == "rs2.med.v6") {
            scrollToElement(".submit-button");
            $('#ip_add').hide();
            $('#abj_nei').hide();
            $('#los_nei').hide();
            $('#ip_address').removeAttr('required');
            $('#ip_address').removeAttr('data-error');
            $('#abj_neighbors').removeAttr('required');
            $('#abj_neighbors').removeAttr('data-error');
            $('#los_neighbors').removeAttr('required');
            $('#los_neighbors').removeAttr('data-error');
            $('#los_nei_v6').show();
            $('#los_neighbors_v6').attr('required', '');
            $('#los_neighbors_v6').attr('data-error', 'This field is required');

        }else if (selected_command == 'ping' || selected_command == 'traceroute' || selected_command == 'route' || selected_command =='route_detail'){
            scrollToElement(".submit-button");
            $('#ip_add').show();
            $('#ip_address').attr('required', '');
            $('#ip_address').attr('data-error', 'This field is required.');
            $('#abj_nei').hide();
            $('#los_nei').hide();
            $('#los_nei_v6').hide();
            $('#los_neighbors_v6').removeAttr('required');
            $('#los_neighbors_v6').removeAttr('data-error');
            $('#los_neighbors').removeAttr('required');
            $('#los_neighbors').removeAttr('data-error');
            $('#abj_neighbors').removeAttr('required');
            $('#abj_neighbors').removeAttr('data-error');
        }
    })
});

function resetForm() {
    $('.loading').hide();
    $('#output').show();
    $('.btn').prop("disabled",false);
    $("select").each(function() { this.selectedIndex = 0 });
    $("input[type=text]").val("");
    $('#los_nei').hide();
    $('#los_nei_v6').hide();
    $('#abj_nei').hide();
    $('#ip_add').hide();
    $('#ip_address').removeAttr('required');
    $('#ip_address').removeAttr('data-error');
    $('#los_neighbors').removeAttr('required');
    $('#los_neighbors').removeAttr('data-error');
    $('#los_neighbors_v6').removeAttr('required');
    $('#los_neighbors_v6').removeAttr('data-error');
    $('#abj_neighbors').removeAttr('required');
    $('#abj_neighbors').removeAttr('data-error');
}



$('#formOne').on('submit', function(e){
    e.preventDefault();
    $('.loading').css("display", "block");
    $('#output').hide();
    $('.btn').prop("disabled",true);
    scrollToElement(".loading");

    $.ajax({
       type : "GET", 
       url: $(this).attr('action') + $('#command').find(":selected").val() + '/',
       data: {
        ip_address : $('#ip_address').val(),
        command: $('#command').find(":selected").val(),
        los_neighbors: $('#los_neighbors').find(":selected").val(),
        los_neighbors_v6: $('#los_neighbors_v6').find(":selected").val(),
        abj_neighbors: $('#abj_neighbors').find(":selected").val(),
        server: $('#server').find(":selected").val(),
        dataType: "json",

       },

       success: function(data){
        resetForm();
        $('#output').html(data.result);
        scrollToElement("#output"); 
       },
       
       error: function(XMLHttpRequest, textStatus, errorThrown) { 
           resetForm();
           $('#output').html(`<p class="text-danger text-center">${errorThrown}</p>`)

        }      
    });
});     
