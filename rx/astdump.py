#!/usr/bin/env python
"""
Module to play with Abstract Syntax Tree (AST) of Python scripts.

For example, you can get version information and other distutils
metadata without importing anything::

  $ astdump.py --topvars astdump.py

"""
__author__ = 'anatoly techtonik <techtonik@gmail.com>'
__version__ = '4.2'
__license__ = 'Public Domain'
__description__ = 'Extract information from Python modules without importing'


import ast
import sys


def propnames(node):
  """return names of attributes specific for the current node"""
  return [x for x in dir(node) if not x.startswith('_')
                                  and x not in ['col_offset', 'lineno']]

def dumpattrs(node, indent=0, oneline=False, output=sys.stdout):
  """
  Dump attributes of given node to `output` (sys.stdout by default).
  If `oneline` is set, format output as one line. Otherwise dump one
  attribute per line with the given `indent`.
  """
  outlines = []
  for n in propnames(node):
    outlines.append("%s: %s" % (n, node.__dict__[n]))
  if not oneline:
    output.write(" "*indent + ("\n"+" "*indent).join(outlines))
    output.write("\n")
  else:
    output.write("[%s]\n" % ", ".join(outlines))


class TreeDumper(ast.NodeVisitor):
  def dump(self, node, types=[], limit=None, callback=None):
    """walk AST tree and exec callback for each matched node

       if `types` is set, process only types in the list
       use `limit` to prevent walking below given depth
       `callback` (if set) will be called to process filtered
         node. callback receives two parameters - node and
         list of parent nodes (stack)
    """
    self.types = types
    self.limit = limit
    self.stack = []
    self.callback = callback or (lambda x, y: None)
    self.visit(node)

  def visit(self, node):
    """this function is called automatically"""
    nodetype = type(node)
    if not self.types or nodetype in self.types:
      self.callback(node, self.stack)
    self.stack.append(node)
    if self.limit == None or self.depth <= self.limit:
      self.generic_visit(node)
    self.stack.pop()

  @property
  def depth(self):
    return len(self.stack)

# --- Callbacks ---
def printcb(node, stack):
  '''print indented node names'''
  nodename = node.__class__.__name__
  print(' '*len(stack)*2 + nodename)

def buffercb(node, stack, buffer):
  '''append indented node names to list buffer'''
  nodename = node.__class__.__name__
  buffer.append(' '*len(stack)*2 + nodename)
  
def printassign(node, stack):
  nodename = node.__class__.__name__
  print(nodename)
  dumpattrs(node, 1)
#--- /Callbacks ---


def top_level_vars(filename):
  """Return name/value pairs for top level variables for the script specified as `filename`.
     Only string and int values are supported.
  """
  root = read_ast(filename)
  return node_top_level_vars(root)

def node_top_level_vars(root):
  """
  Return dict with top level variables for the given node. Only string and
  int values are supported.
  """
  variables = {}
  def get_vars_cb(node, stack):
    if type(node) != ast.Assign:
      return
    if type(node.value) not in [ast.Str, ast.Num]:
      return
    for t in node.targets:  # all targets are of Name type
      #print(" " + type(t).__name__)
      #dumpattrs(t, 2)
      name = t.id
      #dumpattrs(node.value, 2)
      #print(type(t), type(t) == ast.Name, type(t).__name__)
      if type(node.value) == ast.Str:
        variables[name] = node.value.s
      elif type(node.value) == ast.Num:
        variables[name] = node.value.n

  TreeDumper().dump(root, types=[ast.Assign], limit=1, callback=get_vars_cb)
  return variables


def read_ast(filename):
  """Read filename and return root node of the AST"""
  return ast.parse(open(filename).read(), filename)


setup_template = """
#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'astdump',
    version = '{{ version }}',
    author = '{{ author }}',
    author_email = '{{ author_email }}',
    description = '{{ description }}',
    long_description = open('README.rst', 'rb').read(),
    license = 'Public Domain',
    url='https://bitbucket.org/techtonik/astdump',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: Public Domain',
        'Topic :: Software Development',
        'Topic :: Software Development :: Disassemblers',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    py_modules=['astdump'],
)

"""

def get_setup_py(filename, lookup=True):
  """
  Generate setup.py from information extracted from `filename`.
  If `lookup` is True, an attempt to get initial metadata from
  PyPI is made.
  """

  # --- parse AST, get props ---
  root = read_ast(filename)

  props = node_top_level_vars(root)
  docstring = ast.get_docstring(root)
  name = filename[:-3] if filename.endswith(".py") else filename

  # --- define metadata ---
  meta = {}
  # required fields
  # http://docs.python.org/2/distutils/setupscript.html#additional-meta-data
  required = ['name', 'version', 'author', 'author_email']
  essential = ['description', 'license', 'url']
  processed = ['classifiers']

  # --- lookup existing meta data for the module from PyPI ---
  if lookup:
    try :
      from urllib import urlopen
    except ImportError: # PY3K
      from urllib.request import urlopen
    import json
    try:
      data = urlopen('https://pypi.python.org/pypi/%s/json' % name).read()
      try:
        data = json.loads(data)['info']
      except TypeError: # PY3K
        data = json.loads(data.decode('utf8'))['info']
      # meaningful keys
      keys = required + essential + processed + ['bugtrack_url', 'docs_url',
              'download_url', 'home_page', 'keywords', 'maintainer',
              'maintainer_email', 'requires_python', 'stable_version', 'summary']
      keys.remove('url')   # ugly wart - setup.py:'url' is PyPI:'home_page'
      for k in keys:
        meta[k] = data[k]
      meta['url'] = meta.pop('home_page')
      # more ugly warts
      #  - setup.py:'description' is PyPI:'summary'
      #  - setup.py:'long_description' is PyPI:'description'
      meta['long_description'] = meta.pop('description')
      meta['description'] = meta.pop('summary')
      # insanity check
      if meta['name'] != name:
        raise Exception('Lookup failed')
    except (IOError, ValueError):  # lookup failed
      pass

  if 'name' not in meta:
    meta['name'] = name
  #import pprint; pprint.pprint(meta)

  # --- update meta data with props ---
  if '__version__' in props:
    meta['version'] = props['__version__']

  if '__author__' in props:
    author = props['__author__']
    email = None
    if '@' in author and '<' in author:
      email = author.split('<', 1)[1].strip('>')
      author = author.split('<', 1)[0].strip()
    meta['author']= author
    meta['author_email'] = email

  for field in required:
    if field not in meta.keys():
      raise Exception("Missing required field '%s'" % field)

  # these fields are required
  setup = """\
#!/usr/bin/env python
from distutils.core import setup

setup(
    name = '{name}',
    version = '{version}',
    author = '{author}',
    author_email = '{author_email}',
"""
  setup = setup.format(**meta)

  # these fields are optional
  if '__description__' in props:
    meta['description'] = props['__description__']
  # attempt to use docstring as a description if it is short
  elif docstring and len(docstring.splitlines()) == 1:
    meta['description'] = docstring
    
  for propname in ['__license__', '__url__']:
    if propname in props:
      meta[propname.strip('_')] = props[propname]

  for field in essential:
    if field in meta.keys():
      setup += "    {key} = '{value}',\n".format(key=field, value=meta[field])

  import glob
  longdesc = glob.glob('README.*')
  if longdesc:
    setup += "    long_description = open('%s', 'rb').read(),\n" % longdesc[0]

  if 'classifiers' in meta and meta['classifiers']:
    import pprint
    line = pprint.pformat(meta['classifiers'], indent=8)
    line = line.replace('[', '    classifiers=[\n ')
    setup += line + ','

  setup += """
    py_modules=['{name}']
)""".format(**meta)
  return setup


def indented(text, printres=True):
  '''Format indented AST. Try to do it as pretty as possible.
     If `printres` is set, print output, else return string.
  '''
  root = ast.parse(text)
  if printres:
    TreeDumper().dump(root, callback=printcb)
  else:
    from functools import partial
    buffer = []
    chargedcb = partial(buffercb, buffer=buffer)
    TreeDumper().dump(root, callback=chargedcb)
    return '\n'.join(buffer)


if __name__ == '__main__':
  import optparse  

  parser = optparse.OptionParser(usage="%prog [options] <filename.py>",
             description="AST dump tool to inspect Python source code without "
                         "importing it. Can extract values of top level vars, "
                         "automatically generate setup.py and dump structure "
                         "of an Abstract Syntax Tree in readable format.\n")
  parser.add_option('--topvars', action='store_true',
                              help='get top level variables')
  parser.add_option('--generate', action='store_true',
                              help='generate setup.py for a given filename')
  opts, args = parser.parse_args()
  
  if len(args) == 0:
    parser.print_help()
    sys.exit(-1)
  filename = args[0]

  if opts.topvars:
    topvars = top_level_vars(filename)
    for name in sorted(topvars):
      print(name + ' = ' + repr(topvars[name]))

  elif opts.generate:
    print(get_setup_py(filename))

  else:
    indented(open(filename).read())

  #root = read_ast(filename)
  #print(ast.dump(root, annotate_fields=False))
  #print(ast.dump(root))
  #TreeDumper().dump(root, types=[ast.Assign])
  #TreeDumper().dump(root, types=[ast.Assign], limit=1)
  #TreeDumper().dump(root, types=[ast.Assign], limit=1, callback=printcb)
  #TreeDumper().dump(root, types=[ast.Assign], limit=1, callback=printassign)

# [ ] create YAML representation of ASDL (Zephyr)
# [ ] document dataset handling
