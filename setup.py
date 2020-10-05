from setuptools import setup

setup(
	name = "H-PyMon",
	version = "alpha",
	author = "Vivien WALTER",
	author_email = "walter.vivien@gmail.com",
	description = (
	"Software to connect on a calculation center and check the progress"
	),
	license = "GPL3.0",
	packages=[
	'HPyMon',
	]
	,
	install_requires=[
	'numpy',
	'pandas',
	'paramiko',
	'sshtunnel',
	]
)
