function parseOutput(outputData, command, is_table=0, listOfTableTH=null, table_id=null,  server=null) {
    if (is_table) {
    let protocol_table;
        protocol_table = `<table class="table-sort table-arrows" id="${table_id}"><caption>${server}: 
                            ${command}</caption><thead><tr>`

        listOfTableTH.forEach(item => 
           protocol_table += `<th>${item}</th>`);

        protocol_table += '</tr></thead><tbody>'

        outputData.forEach(protocol => {
            protocol_table += '<tr>'
                listOfTableTH.forEach(item =>
                protocol_table += `<td>${protocol[item]}</td>`)
            protocol_table += '</tr>'

            })

        protocol_table += '</tbody></table><br><br><br>'

        return protocol_table
    }else {
        output = `<br><br>
                <div class="container">
                    <div class="row">
                        <div class="result">
                            <div class="col-sm"><strong>
                                <h4>
                                    <strong>${command}</strong>
                                </h4><br>${outputData}
                                    </strong>
                            </div>
                        </div>
                    </div>
                </div><br><br>`

        return output

    }


        
        
}


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
        let selected_command = $('#id_command').val();
        let selected_server = $('#id_server').val();
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
    command = $('#id_command').find(":selected").val(),

    $.ajax({
       type : "GET", 
       url: $(this).attr('action') + $('#id_command').find(":selected").val() + '/',
       data: {
        ip_address : $('#id_ip_address').val(),
        command: command,
        server: s,
        bgp_peer: $(`#id_${s}_peers`).find(":selected").val(),
        dataType: "json",

       },

       success: function(data){
        resetForm();
        

        $('#output').html(
            parseOutput(
                data.result,
                data.command, 
                data.is_table,
                data.table_header, 
                data.table_id,
                s,
                )
            );
            console.log(data)
            var t = $(`#${data.table_id}`).DataTable({
                columnDefs: [
                  { type: 'ip-address', targets: data.ip_col },
                  { searchable: false, orderable: false, targets: 0},
                  
                ],
                pageLength: 500,
                lengthMenu: [10, 50, 100, 500, 1000],
                order: [[1, 'asc']],
                
             });
             t.on('order.dt search.dt', function () {
                let i = 1;
         
                t.cells(null, 0, { search: 'applied', order: 'applied' }).every(function (cell) {
                    this.data(i++);
                });
            }).draw();
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
            $('#output').html(
                parseOutput(
                    data.result,
                    data.command, 
                    data.is_table,
                    data.table_header, 
                    data.table_id,
                    s,
                    )
                );
                console.log(data)
            var t = $(`#${data.table_id}`).DataTable({
                columnDefs: [
                  { type: 'ip-address', targets: data.ip_col },
                  { searchable: false, orderable: false, targets: 0},
                  
                ],
                pageLength: 500,
                lengthMenu: [10, 50, 100, 500, 1000],
                order: [[1, 'asc']],
                
             });
             t.on('order.dt search.dt', function () {
                let i = 1;
         
                t.cells(null, 0, { search: 'applied', order: 'applied' }).every(function (cell) {
                    this.data(i++);
                });
            }).draw();
            scrollToElement("#output"); 
        },
               
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            resetForm();
            $('#output').html(`<p class="text-danger">&emsp;&emsp;&emsp;${errorThrown}</p>`)
        
        }      
    });
});     
