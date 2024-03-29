from django import forms
import json
from lookingglass.local_settings import commands
from lookingglass.servers import servers
from lookingglass.settings import BASE_DIR


for item in servers:
    with open(f'{BASE_DIR}/lg/{item}.json') as globals()[f'{item}_input']:
        globals()[f'{item}'] = json.load(globals()[f'{item}_input'])


def get_choices(options):
    choices = [('', '----')]
    for key, value in options.items():
        choices.append((key, value[0]))
    return choices

class CommandForm(forms.Form):
    server = forms.ChoiceField(label="Route Server", choices=get_choices(servers))
    command = forms.ChoiceField(choices=get_choices(commands))
    ip_address = forms.CharField(label='Ip address', max_length=60) 
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in servers:
            field_name = f'{i}_peers'
            self.fields[field_name] = forms.ChoiceField(label='BGP Peer', choices=get_choices(globals()[f'{i}']))
 
       