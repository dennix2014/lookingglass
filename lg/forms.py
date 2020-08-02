from django import forms

commmands = ( 
    ("ping", "ping"), 
    ("traceroute", "traceroute"), 
    ("route", "route"), 
    ("route detail", "route detail"), 
) 

protocols = (
    ('ipv4', 'ipv4'),
    ('ipv6', 'ipv6')
)

class CommandForm(forms.Form):
    protocol = forms.ChoiceField(widget=forms.RadioSelect, choices=protocols)
    ip_address = forms.CharField(label='Ip address', max_length=20)
    command = forms.ChoiceField(widget=forms.RadioSelect, choices=commmands)