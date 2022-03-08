import rich
import rich.console
import rich.tree
# import rich.text
import plotille as plt
import os

class Directory:
    def __init__(self, name, dim = False, icon = ':open_file_folder'):
        self.name = name
        self.icon = icon
        self.children = []
        self.dim = dim

    def add(self, child):
        self.children.append(child)

    def pretty_name(self):
        return self.icon + ' ' + self.name

    def make_tree(self):
        if self.dim:
            style = 'dim'
        else:
            style = ''
        tree = rich.tree.Tree(self.pretty_name(), style=style)
        for child in self.children:
            tree.add(child.make_tree())
        return tree


console = rich.console.Console()

directory = Directory('VSim data directory')

if os.path.isdir('data'):
    console.log('Moving into data directory')
    os.chdir('data')

files = os.listdir()
files.sort()

stems = []
dirs = []

for file in files:
    parts = file.split('_')

    if len(parts) == 2:
        stem, ext = parts[1].split('.', 1)
        num = None

        if stem == 'History':
            # icon = ':calendar:'
            icon = ':alarm_clock:'
        else:
            icon = ':page_facing_up:'

        if 'backup' in ext:
            dim = True
        elif ext == '.txt':
            dim = True
        else:
            dim = False

        directory.add(Directory(file, dim, icon))
    elif len(parts) == 3:
        stem = parts[1]
        num, ext = parts[2].split('.', 1)
    else:
        console.log(file)
        continue

# tree.add(':page_facing_up: vsim_History.h5')
# tree.add(':page_facing_up: vsim_History.h5.backup', style='dim')

# etree = rich.tree.Tree(':file_cabinet:  vsim_E_*.h5', guide_style='dim')
# etree.add(':page_facing_up: vsim_E_0.h5')
# etree.add(':page_facing_up: ...')
# etree.add(':page_facing_up: vsim_E_50.h5')
# tree.add(etree)

rich.print(directory.make_tree())
