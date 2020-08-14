from netmiko import ConnectHandler

initial_html = """<div class="container result">
                <div class="row">
	    	    <div class="col-sm">"""

closing_html = """</div></div></div><br>"""

def connect_to_route_server(server, command):
    
    net_connect = ConnectHandler(**server)
    out = net_connect.send_command(command, delay_factor=2)

    output = out.replace('      ', '&emsp;&emsp;').\
        replace('BIRD 1.6.3 ready.\nAccess restricted\n', '').\
        replace('BIRD 1.6.8 ready.\nAccess restricted\n', '').\
        replace('\n', '<br>').replace('\t', '&emsp;&emsp;').\
        replace('   ', '&emsp;&emsp;').\
        replace('    ', '&emsp;&emsp;').\
        replace('     ', '&emsp;&emsp;')

    final_html = initial_html
    final_html += f'<strong>Command: {command}</strong><br><br>'

    final_html += output
    final_html += closing_html
    return final_html
