#mysetup.py

from distutils.core import setup
import py2exe

#setup(windows=["E:\\src\\mainframe.py"],options = { "py2exe":{"dll_excludes":["MSVCP90.dll"]}})

includes = ["encodings", "encodings.*"]

options = {"py2exe":
            {"compressed": 1,
             "optimize": 2,
             "ascii": 1,
             "includes":includes,
             "bundle_files": 1
            }}
setup(
    #options=options,
    zipfile=None,
    #console=[{"script": "HelloPy2exe.py", "icon_resources": [(1, "pc.ico")]}],
    windows=[{"script": "CProfileGetTool.py", "icon_resources": [(1, "pc.ico")]}],
    options = { "py2exe":{"dll_excludes":["MSVCP90.dll"]}}

)
