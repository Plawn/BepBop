import re
string = """
export default [download_folder_div,
    parsers_folder_div,
    port_input,
    darkmode_toggle_button,
    input_login,
    input_password];
"""


re_js_exporter = re.compile(r"(?s)(?<=export default ).*?(?=])")


def check_export_string(i: str):
    i = i.strip()
    if i[0] == '[':
        i = i[1:]
    if i[-1] == ']':
        i = i[:-1]
    return i


def build_export_string(string):
    res = re_js_exporter.findall(string)
    if len(res) > 0 :
        res = res[0]
    else :
        return ''
    s = ''
    for i in [check_export_string(i) for i in res.split(',')]:
        s += 'window.{} = {};\n'.format(i, i)
    return s


s = build_export_string(string)

print(s)
