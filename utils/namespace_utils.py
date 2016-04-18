__author__ = 'Po'

import sys
import atexit
import socket
import weakref
import importlib
import rpyc
import rpyc.core.service as Service
import rpyc.core.protocol as Protocol
import rpyc.utils.factory as Factory


namespace_registry = dict() # <key : value> == <namespace : NamespaceManager instance>


def _clear_all():
	try:
		for namespace, manager in namespace_registry.items():
			assert isinstance(manager, NamespaceManager)
			manager.close()
	except:
		pass


# Auto close all connections and stop background threads.
atexit.register(_clear_all)


class _ModifiedModuleNamespace(Service.ModuleNamespace):
	"""
	Enable setattr to ModuleNamespace which is necessary to make
	ModuleNamespace as a virtual module.
	"""
	pass


Service.ModuleNamespace = _ModifiedModuleNamespace


class _ModifiedConnection(Protocol.Connection):
	"""
	Add error_handler to Connection.
	"""

	def _send(self, msg, seq, args):
		try:
			return super(_ModifiedConnection, self)._send(msg, seq, args)
		except Exception as ex:
			error_handler = getattr(self, 'error_handler', None)
			if callable(error_handler) and error_handler(self, ex):
				return
			else:
				raise ex

	def _recv(self, timeout, wait_for_lock):
		try:
			return super(_ModifiedConnection, self)._recv(timeout, wait_for_lock)
		except Exception as ex:
			error_handler = getattr(self, 'error_handler', None)
			if callable(error_handler) and error_handler(self, ex):
				return
			else:
				return


Factory.Connection = _ModifiedConnection


class RemoteImporter(object):
	"""
	A meta_path hooker to import remote module from conn in namespace.
	"""

	def __init__(self, conn, namespace):
		self.conn = conn
		self.namespace = namespace
		modules = conn.modules
		modules.__path__ = [namespace] # module should have __path__ attribute.
		sys.modules[namespace] = modules

	def find_module(self, fullname, path=None):
		if fullname.partition('.')[0] == self.namespace:
			# If import module in namespace, use self as module loader.
			return self
		return None

	def load_module(self, fullname):
		name = fullname.partition('.')[2]
		modules = self.conn.modules
		module = modules[name]
		if not hasattr(module, '__path__'):
			# This is nessisary to make ModuleNamespace as a package, but
			# will make all remote modules as packages.
			module.__path__ = ''
		if '.' not in name:
			# This is nessisary to make ModuleNamespace as a virtual module.
			setattr(modules, name, module)
		# Avoid reimport the same module, builtin importer will search sys.modules automatically.
		sys.modules[fullname] = module
		return module


class NamespaceManager(object):
	"""
	A namespace manager to hold connection, background thread and remote importer.
	"""

	def __init__(self, conn, remote_importer):
		conn.error_handler = self.error_handler
		self.conn = conn
		self.bgsrv = rpyc.BgServingThread(conn)
		self.remote_importer = remote_importer

		namespace_registry[remote_importer.namespace] = self

	def __del__(self):
		self.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def close(self):
		"""
		will:
		1, remove self from namespace registry;
		2, remove self.remote_importer from sys.meta_path, and set self.remote_importer to None;
		3, stop background thread self.bgsrv, and set self.bgserv to None;
		4, close connection self.conn, and set self.conn to None;

		won't:
		clear modules of namespace.

		You didn't *nearly* reset Python to the state in which it was before the import:
		the modules that got imported recursively still hang in sys.modules.

		Please accept that Python indeed does not support unloading modules for severe,
		fundamental, insurmountable, technical problems, in 2.x.

		In 3.x, chances are slightly higher. In principle, unloading could be supported -
		but no module actually adds the necessary code, and the necessary code in the import
		machinery isn't implemented in 3.2 and earlier.

		Supporting unloading will be (and was) a multi-year project. Don't expect any
		results in the next five years.
		"""
		if self.remote_importer:
			namespace = self.remote_importer.namespace
			# Remove self from namespace_registry.
			if namespace in namespace_registry:
				del namespace_registry[namespace]

		try:
			# Remove old RemoteImporter of namespace in sys.meta_path
			sys.meta_path.remove(self.remote_importer)
		except:
			pass
		finally:
			self.remote_importer = None

		if self.bgsrv:
			try:
				self.bgsrv.stop()
			except AssertionError:
				pass
			finally:
				self.bgsrv = None

		if self.conn:
			self.conn.close()
			self.conn = None

	@classmethod
	def connect(cls, host='localhost', port=18812, namespace='x9'):
		"""
		Launch a classic connect to host: port as namespace,
			import <namespace> as ns
				=> ns will be connect.modules
			from <namespace>.debug import draw
				=> will import connect.modules['debug.draw'] as draw

		If connect twice to the same namespace,
			1, all imported modules will alive and use the latest connection;
			2, all old remote objects will die;
			3, old NamespaceManager will be closed automatically.
		"""

		try:
			conn = rpyc.classic.connect(host, port)
		except socket.error:
			return None
		remote_importer = RemoteImporter(conn, namespace)

		# Update all imported remote modules.
		manager = namespace_registry.get(namespace)
		if manager:
			manager.close()

		sys.meta_path.append(remote_importer)
		sys.modules[namespace] = conn.modules
		cls.update_modules(namespace)

		return cls(conn, remote_importer)

	@classmethod
	def update_modules(cls, namespace):
		"""
		Update imported modules by namespace.
		"""
		module_backup = dict()
		match_key = namespace + '.'
		for name, module in sys.modules.iteritems():
			if name.startswith(match_key):
				module_backup[name] = module

		for name in module_backup.iterkeys():
			del sys.modules[name]

		for name, module in module_backup.iteritems():
			new_module = importlib.import_module(name)
			conn = object.__getattribute__(new_module, "____conn__")()
			oid = object.__getattribute__(new_module, "____oid__")
			object.__setattr__(module, "____conn__", weakref.ref(conn))
			object.__setattr__(module, "____oid__", oid)

		for name, module in module_backup.iteritems():
			sys.modules[name] = module

	def error_handler(self, sender, ex):
		pass


class AutoCloseNM(NamespaceManager):

	def error_handler(self, sender, ex):
		self.close()
		return True

# ------------------------------------------------------------------
# Define global connections here or use below when you needs:

# with NamespaceManager.connect('localhost', 18813, 'tmp') as ns:
#     # This module name should be different from global modules.
#     from tmp import BigWorld as tmp_bw

#     # Make sure your remote call is a sync operation! For example,
#     # tmp_bw.callback will be failed after this NamespaceManager exit.
#     tmp_bw.dcursor().yaw = 1

