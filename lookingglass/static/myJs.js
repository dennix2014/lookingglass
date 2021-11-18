function scrollToElement(id_or_class){
    $('html, body').animate({
        scrollTop: $(id_or_class).offset().top
    }, 1000);
}

function hideArrayOfElemets(arrayOfElemets) {
    arrayOfElemets.forEach(element =>  $(`#div_id_${element}_peers`).hide());
    arrayOfElemets.forEach(element =>  $(`#div_id_${element}_peers`).parent().hide());
    arrayOfElemets.forEach(element =>  $(`#id_${element}_peers`).removeAttr('required'));
    arrayOfElemets.forEach(element =>  $(`#id_${element}_peers`).removeAttr('data-error'));
}

function hideElement(element) {
    $(`#div_${element}`).hide();
    $(`#div_${element}`).parent().hide();
    $(`#${element}`).removeAttr('required');
    $(`#${element}`).removeAttr('data-error');
}


$(document).ready(function() {
    let serverz = $('#serverz').attr('servers')
    serverz = (serverz.substring(1, serverz.length-1)+',').split(' ');
    serverz.forEach( (item,i) => serverz[i] = item.substring(1, item.length-2));
    resetForm()
    
    $("#id_command, #id_server").on('load change', function() {
        var selected_command = $('#id_command').val();
        var selected_server = $('#id_server').val();
        if (selected_command == 'bgp_neighbors') {
            hideElement('id_ip_address')
            hideArrayOfElemets(serverz)

        } else if (selected_command == 'bgp_neighbor_received'){
            scrollToElement("#id_command");
            hideElement('id_ip_address')
            serverz.forEach(server =>  {
                if (server != selected_server) {
                    $(`#div_id_${server}_peers`).hide();
                    $(`#div_id_${server}_peers`).parent().hide();
                    $(`#id_${server}_peers`).removeAttr('required');
                    $(`#id_${server}_peers`).removeAttr('data-error');
                }else if (server == selected_server) {
                    $(`#div_id_${selected_server}_peers`).show();
                    $(`#div_id_${selected_server}_peers`).parent().show();
                    $(`#id_${selected_server}_peers`).attr('required', '');
                    $(`#id_${selected_server}_peers`).attr('data-error', 'This field is required');
                }
            });

        }else if (selected_command == 'ping' || selected_command == 'traceroute' || selected_command == 'route' || selected_command =='route_detail'){
            scrollToElement("#id_command");
            $('#div_id_ip_address').show();
            $('#div_id_ip_address').parent().show();
            $('#id_ip_address').attr('required', '');
            $('#id_ip_address').attr('data-error', 'This field is required.');
            hideArrayOfElemets(serverz)
        }
    })
});

function resetForm() {
    let serverz = $('#serverz').attr('servers')
    serverz = (serverz.substring(1, serverz.length-1)+',').split(' ');
    serverz.forEach( (item,i) => serverz[i] = item.substring(1, item.length-2));
    $('.loading').hide();
    $('#output').show();
    $('.btn').prop("disabled",false);
    $("select").each(function() { this.selectedIndex = 0 });
    $("input[type=text]").val("");
    hideElement('id_ip_address')
    hideArrayOfElemets(serverz)
    
}



$('#formOne').on('submit', function(e){
    e.preventDefault();
    $('.loading').css("display", "block");
    $('#output').hide();
    $('.btn').prop("disabled",true);
    scrollToElement(".loading");
    s = $('#id_server').find(":selected").val()

    $.ajax({
       type : "GET", 
       url: $(this).attr('action') + $('#id_command').find(":selected").val() + '/',
       data: {
        ip_address : $('#id_ip_address').val(),
        command: $('#id_command').find(":selected").val(),
        server: s,
        bgp_peer: $(`#id_${s}_peers`).find(":selected").val(),
        dataType: "json",

       },

       success: function(data){
        resetForm();
        $('#output').html(data.result);
        scrollToElement("#output"); 
       },
       
       error: function(XMLHttpRequest, textStatus, errorThrown) { 
           resetForm();
           $('#output').html(`<p class="text-danger">&emsp;&emsp;&emsp;${errorThrown}</p>`)

        }      
    });
});     


$(document).on('click', '.received-routes', function(){
    $('.loading').css("display", "block");
    $('#output').hide();
    $('.btn').prop("disabled",true);
    scrollToElement(".loading");
    let server = $('caption').text().split(':')[0];
    let bgp_peer = $(this).closest('tr').find('td:nth-child(2)').text();
    if (server.includes('v6')) {
        bgp_peer = bgp_peer.split(':')[0]
    }
    $.ajax({
        type : "GET", 
        url : 'bgp_neighbor_received/',
        data: {
            command: 'bgp_neighbor_received',
            server: server,
            bgp_peer: bgp_peer,
            dataType: "json",
        
        },
        
        success: function(data){
            resetForm();
            $('#output').html(data.result);
            scrollToElement("#output"); 
        },
               
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            resetForm();
            $('#output').html(`<p class="text-danger">&emsp;&emsp;&emsp;${errorThrown}</p>`)
        
        }      
    });
});     
