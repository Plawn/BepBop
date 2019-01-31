import os
import json
import shutil
import re
import Fancy_term as term
# add watcher for auto recompile

print_error = term.Smart_print(style=term.Style(
    color=term.colors.red, substyle="bold"))
print_success = term.Smart_print(style=term.Style(
    color=term.colors.green, substyle="bold"))


loader_replace = '//put the loader here//'
# regex
re_classes = re.compile(r"\.-?[_a-zA-Z]+[_a-zA-Z0-9-]*\s*\{")
re_ids = re.compile(r"\#[a-z]+[0-9]*")

begin = """(function (){
            const home = new Fancy_router.Panel(null, { name: '%s' });\n"""
end = """r.render();\n})();"""

# filenames
html_name = 'page.html'
css_name = 'page.css'
settings_name = 'settings.json'
onload_name = 'onload.js'
js_name = 'page.js'

# presets


def do_one_page(folder_name):

    with open(os.path.join(folder_name, html_name)) as f:
        html = f.read()

    with open(os.path.join(folder_name, onload_name)) as f:
        js = f.read()

    is_home = False
    with open(os.path.join(folder_name, settings_name), 'r') as f:
        settings = json.load(f)
        if 'is_home' in settings:
            is_home: bool = True
        order: int = settings['order']

    # handling css here
    filename = os.path.join(folder_name, css_name)
    css = None
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            css = f.read()

    # handling js here
    filename = os.path.join(folder_name, js_name)
    js_content = None
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            js_content = f.read()
    return {'content': html, 'onload': js}, order, is_home, css, js_content, folder_name.split('/')[-1], folder_name


def build_loader(home_page, folders, map_name, map_home):
    s = begin % home_page[5]
    names_l = ['p'+str(i) for i in range(len(folders))]
    names = ','.join(names_l)
    for i, folder in enumerate(folders):
        s += "const %s = " % ('p'+str(i)) + \
            "new Fancy_router.Panel(null, { name: '%s' });\n" % folder.split(
                '/')[-1]
    # home is in begin
    s += "const l = new Fancy_router.Loader([{}],'{}');\n".format(
        names, map_name)

    s += "const home_loader = new Fancy_router.Loader([home], '%s', { next_loader: l });\n" % map_home
    
    names_l.insert(home_page[1], 'home')
    names = ','.join(names_l)
    s += 'home_loader.load();'
    
    s += "const r = new Fancy_router.Renderer(document.getElementById('main_container'), [{}], {});".format(
        names, '{home_value : %s }' % home_page[1])

    s += end
    return s

# css building


def css_checker(classes, ids):
    if len(classes) == len(set(classes)):
        if len(ids) == len(set(ids)):
            return True
    return False


def get_classes(css):
    return list(map(lambda x: x[1:-1],  re_classes.findall(css)))


def get_ids(css):
    return list(map(lambda x: x[1:], re_ids.findall(css)))


def handle_css(folders, output, fold):
    css, ids, classes = '', [], []

    for item, folde in zip(filter(lambda x: x != None, map(lambda x: x[3], folders)), fold):
        ids += get_ids(item)
        classes += get_classes(item)
        if css_checker(ids, classes):
            css += item
        else:
            raise Exception(
                'classe or id duplicate trying to add : "{}" page'.format(folde.split('/')[-1]))
    with open(os.path.join(os.path.dirname(output), 'index.css'), 'w') as f:
        f.write(css)


# js building
def handle_js(folders, output, fold):
    js = ''
    # variables = []
    for item in filter(lambda x: x[4] != None, folders):
        js += item[4] + '\n'
    return js

# add support for the first page


def build_home_map(page, filename):
    with open(filename, 'w') as f:
        json.dump({page[5]: page[0]}, f, indent=4)


def compile_directory(folders, output, output_home):
    res = [do_one_page(folder) for folder in folders]
    res.sort(key=lambda x: x[1])
    # handling home page
    try:
        home_page = list(filter(lambda x: x[2], res))[0]
    except:
        raise Exception('No homepage set')
    # fold.remove(home_page[6])
    build_home_map(home_page, output_home)
    # css handling
    handle_css(res, output, folders)  # css of homepage with the rest for now
    res.remove(home_page)
    js = handle_js(res, output, folders)
    d = {i[5]: i[0] for i in res}
    d['js'] = js

    with open(output, 'w') as f:
        json.dump(d, f, indent=4)
    return home_page, res
# add static directory for router and img


def init_build_directory():
    if os.path.exists('build'):
        shutil.rmtree('build')
    os.mkdir('build')
    shutil.copy('pages/index.js', 'build/')


def build_html(build_path, js):
    with open('build_tools/index.html', 'r') as f:
        content = f.read()
    content = content.replace(loader_replace, js)
    with open(os.path.join(build_path, 'index.html'), 'w') as f:
        f.write(content)


if __name__ == "__main__":
    # content_directory = sys.argv[1]
    content_directory = 'pages'
    build_directory = 'build'
    map_name = 'map.json'
    js_name = 'index.js'
    map_home = 'home_map.json'

    init_build_directory()
    folders = [os.path.join(content_directory, i)
               for i in os.listdir(content_directory)]
    folders.remove('pages/index.js')
    res = None # to shutdown the linter about not def
    try:
        home_page, res = compile_directory(folders, os.path.join(
            build_directory, map_name), os.path.join(build_directory, map_home))
        loader = build_loader(home_page, [i[6] for i in res], map_name, map_home)
        build_html(build_directory, loader)
    except Exception as e:
        print_error('[Error] :', e.__str__())
    else:
        print_success('Success')


