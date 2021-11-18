How to add and modify servers to Lookingglass

Section One: (To be done on the Bird server)
    1.Verify that ping and traceroute utilities are installed, if not install them. 
    The version does not really matter.

    2. Create an account with limited privilege and create an exception for it 
    that will allow it run birdc or birdc6 show commands. 
    The account MUST match credentials being used on other bird servers.
    On Ubuntu 20 server, this is accomplished as follows:
        ##Create user
            sudo adduser <username>
        ## create an exception for running birdc show commands, 
            sudo visudo ## then add the following line
            lg        ALL=(ALL)       NOPASSWD: <birdc path> -r *
            

    3. Create the following aliases. 
    Aliases ensure that same command is called regardless of 
    the ip protocol or version of ping, traceroute or birdc installed. 
    Verify that they are working.

        Command                         |      Alias
        ping -c 5 -i 0.2                |      ping    
        traceroute -n                   |      traceroute
        birdc(6) show route for         |      please show route for
        birdc(6) show protocols all     |      please show protocols all 
        birdc(6) show route protocol    |      please show route protocol              

    
Section TWO: (To be done on the lookingglass server)
    1. Enable password-less ssh login from the lookingglass server to the new bird server. 
    This is to improve lookup time. Verify when you are done.
        ssh-copy-id -p <ssh-port> user@birdserver.

    2. Then add the server to the list of servers in the project settings file. 
    The file is /home/noc-admin/lookingglass/lookingglass/local_settings.py.
    You must Mirror exisiting entries.

    3. Generate list of BGP peers on the server by visiting the follwoing url.
    https://lg.ixp.net.ng/ifendiobodonemedikaikpokundimuo/. 
    This shoudl take a minute or therabout.

    4. Then restart the lookingglass service.
        sudo systemctl restart lookingglass

Al other maintenance activities are automated and dynamic.
