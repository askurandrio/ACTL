import importlib


def importFrom(arg):
	try:
		from_ = arg['from']
		import_ = arg['import']
	except KeyError as ex:
		raise RuntimeError(
			f'Error during getting py-execExternalFunction: {arg}'
		) from ex

	try:
		from_ = importlib.import_module(from_)
	except ImportError as ex:
		raise RuntimeError(
			f'Error importing from_ at py-execExternalFunction: {arg}'
		) from ex

	try:
		return getattr(from_, import_)
	except AttributeError as ex:
		raise RuntimeError(
			f'Error getting {import_} at py-execExternalFunction: {arg}'
		) from ex
