__author__ = 'Po'

from .namespace_utils import *

port = 18812
'''
if len(sys.argv) > 1:
	try:
		port = int(sys.argv[1])
	except:
		pass
'''
default = NamespaceManager.connect(port=port) # Map localhost: 18812 to namespace x9.

# Simple testcase.
#
# from x9.debug import draw as a
# from x9.debug import draw as b
# import x9.avolume.halo as c
# import x9.avolume.halo as d
# from x9 import debug as e
# import x9
#
# print a, b, c, d, e, x9
