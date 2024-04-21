function parseOutput(outputData, command, is_table=0, listOfTableTH=null, table_id=null,  server=null, peerProtocol=null) {
    if (is_table) {
    let protocol_table;
    const he_url = 'https://bgp.he.net/AS'
        protocol_table = `<table class="table-sort table-arrows" id="${table_id}"><caption>${server}: 
                            ${command}</caption><thead><tr>`
        protocol_table += '<th>s/no</th>'
        listOfTableTH.forEach((item) => {
            if (item == 'protocol') {
                protocol_table += `<th class="hidden">${item}</th>`
            }else if (item == 'is_primary') {
            protocol_table += `<th>Remarks</th>`
            }else {
           protocol_table += `<th>${item}</th>`
            }
        });

        protocol_table += '</tr></thead><tbody>'

        let sno = 0
        outputData.forEach(protocol => {
            sno ++
            protocol_table += `<tr><td>${sno}</td>`
            listOfTableTH.forEach((item) => {
                let isFiltered = protocol['is_filtered']
                let isPrimary = protocol['is_primary']
                let prefix = protocol['prefix']
                let param = protocol[item]
                if (item == 'asn') {
                    protocol_table += `<td><a href="${he_url}${param}" target="_blank" rel="noopener noreferrer">${param}</a></td>`
                }else if (item == 'is_primary' && isPrimary && isFiltered){
                    protocol_table += `<td><span><i class="fa-solid fa-triangle-exclamation"></i></span>&emsp;<span class="badge badge-success">P</span></td>`
                }else if (item == 'is_primary' && !isFiltered && isPrimary){
                    protocol_table += `<td><span class="badge badge-success">P</span></td>`
                }else if (item == 'is_primary' && isFiltered && !isPrimary ) {
                    protocol_table += `<td><span><i class="fa-solid fa-triangle-exclamation"></i></span>&emsp;<span class="badge badge-warning">N</span></td>`
                }else if (item == 'is_primary' && !isFiltered && !isPrimary){
                    protocol_table += `<td><span class="badge badge-warning">N</span></td>`
                }else if (item == 'bgp_state' && param == 'Established') {
                    protocol_table += `<td><span class="green">${param}</span></td>`
                }else if (item == 'bgp_state') {
                    protocol_table += `<td><span class="red">${param}</span></td>`
                }else if (item == 'imported' && param <= 1000 && param > 0) {
                    protocol_table += `<td><span class="received-routes"><a href="#">${param}</a></span></td>`
                }else if (item == 'path') {
                    let paths = ''
                    param.forEach((path) => {
                        paths += `<a href="${he_url}${path}" target="_blank" rel="noopener noreferrer">${path}</a> `
                    })
                    protocol_table += `<td>${paths}</td>`
                }else if (item == 'protocol') {
                    protocol_table += `<td class="hidden">${param}</td>`
                }else if (item == 'detail') {
                    protocol_table += `<td><a class="btn btn-outline-secondary show-route-detail" data-toggle="modal"  data-target="#routeDetailModal">
                                            Details
                                        </a></td>
                                        <!-- Modal -->
                                        <div class="modal fade" id="routeDetailModal" tabindex="-1" role="dialog" aria-labelledby="routeDetailModalLabel" aria-hidden="true">
                                          <div class="modal-dialog modal-lg" role="document">
                                            <div class="modal-content">
                                              <div class="modal-header">
                                                <h5 class="modal-title" id="routeDetailModalLabel"></h5>
                                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                                  <span aria-hidden="true">&times;</span>
                                                </button>
                                              </div>
                                              <div class="modal-body">

                                              </div>
                                              <div class="modal-footer">
                                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                                              </div>
                                            </div>
                                          </div>
                                        </div>`
                }else {
                    protocol_table += `<td>${param}</td>` 
                    
                }
            })
            protocol_table += '</tr>'

            })
            protocol_table += '</tbody></table><br><br><br>'
            if (peerProtocol) {
                protocol_table += `
                <input
                type="hidden"
                id="peerProtocol"
                data-peerProtocol="${peerProtocol}"
            />`
            }
        return protocol_table
    }else {
        output = `<br><br>
                <div class="container">
                    <div class="row">
                        <div class="result">
                            <div class="col-sm"><strong>
                                <h4>
                                    <strong>${command}</strong>
                                    <br>
                                </h4><pre>${outputData}</pre>
                                    </strong>
                            </div>
                        </div>
                    </div>
                </div><br><br>`

        return output

    }


        
        
}
function addClass(listItem, text) {
    if (listItem == 1101) {
        return `&emsp;<span class="badge badge-danger">${text}</span>`
    }else if (listItem == 1000 && text.includes("RPKI VALID")) {
        return `&emsp;<span class="badge badge-success">${text}</span>`   
    }else if (listItem == 1001 && text.includes("IRRDB VALID")) {
        return `&emsp;<span class="badge badge-success">${text}</span>`   
    }else {
        return `&emsp;<span class="badge badge-info">${text}</span>`
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
    command = $('#id_command').find(":selected").val()
    protocol = $(`#id_${s}_peers`).find(":selected").val()
    peer = $(`#id_${s}_peers`).find(":selected").text()
    prefix = $('#id_ip_address').val()
    url = $(this).attr('action') + $('#id_command').find(":selected").val() + '/',

    console.log(peer)

    $.ajax({
       type : "GET", 
       url: url,
       data: {
        prefix : prefix,
        command: command,
        server: s,
        protocol: protocol,
        peer: peer,
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
    let protocol = $(this).closest('tr').find('td:nth-child(8)').text();
    let peer = $(this).closest('tr').find('td:nth-child(2)').text();
    
    
    $.ajax({
        type : "GET", 
        url : 'bgp_neighbor_received/',
        data: {
            command: 'bgp_neighbor_received',
            server: server,
            protocol: protocol,
            peer: peer,
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
                    protocol
                    )
                );
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


$(document).on('click', '.show-route-detail', function(){
    $('.btn').prop("disabled",true);
    let server = $('caption').text().split(':')[0];
    let prefix = $(this).closest('tr').find('td:nth-child(2)').text();
    let peerProtocol = $("#peerProtocol").attr("data-peerProtocol");
    
    
    $.ajax({
        type : "GET", 
        url : 'route_detail/',
        data: {
            server: server,
            protocol: peerProtocol,
            prefix: prefix,
            dataType: "json",
        
        },
        
        success: function(data){
            $('.btn').prop("disabled",false);
            let output = data.result[0]    

        let routeRouteDetailHTML = ''

        routeRouteDetailHTML += `
                <table><tbody>
                    <tr>
                        <td>Network</td>
                        <td>${output.prefix}</td>
                    </tr>
                    <tr>
                        <td>Gateway</td>`
                        let isPrimary = output.is_primary
                        if (isPrimary) {
                            routeRouteDetailHTML += `<td>${output.gateway}
                            &emsp;<span class="badge badge-success">Primary</span></td></tr>`
                        }else {
                            routeRouteDetailHTML += `<td>${output.gateway}
                            &emsp;<span class="badge badge-warning">Not Primary</span></td></tr>`
                        }
        routeRouteDetailHTML += `
                    <tr>
                        <td>AS Path</td>
                        <td>${output.as_path}</td>
                    </tr>
                    <tr>`
                    let nextHop = output.next_hop
                    if (nextHop) {
                        routeRouteDetailHTML += `
                        <td>Next Hop</td>
                        <td>${nextHop}</td></tr>`
                    }
                        
                    let largeCommunities = ''
                    let largeCommunitiesOutput = output.large_communities
                    largeCommunitiesOutput.forEach((item) => {
                        largeCommunities += `${item[0]}:${item[1]}:${item[2]}  
                                                ${addClass(item[1],(item[3]))}<hr>`
                    })
                    routeRouteDetailHTML += `
                                            <tr>
                                            <td>Large Communities</td><td>${largeCommunities}</td>
                                            </tr></tbody></table>`

            $('.modal-body').html(routeRouteDetailHTML);
            $('.modal-title').text(`Route Details - ${output.prefix}`)
            $('#routeDetailModal').on('shown.bs.modal', function () {
                $('.modal-body').html(routeRouteDetailHTML);
              });
        


            
        },
               
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            resetForm();
            $('#output').html(`<p class="text-danger">&emsp;&emsp;&emsp;${errorThrown}</p>`)
        
        }      
    });
});    