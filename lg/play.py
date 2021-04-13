import re
nl = '\n'
def split_on_empty_lines(s):
    
    # greedily match 2 or more new-lines
    blank_line_regex = r"(?:\r?\n){2,}"
    return re.split(blank_line_regex, s.strip())


with open('/home/uchechukwu/Documents/members_in_rc.txt') as result:
    a = result.read()

    for item in a.splitlines():
        print(f'<option value="{item}">{item.upper()}</optiom>')