from setuptools import setup,find_packages

setup (
  name = 'AWSApp',
  version = '0.1',
  install_requires = {'Boto':'boto>=1.8','Nose':'nose>=0.11',
      'PyCrypto':'pycrypto>=2.0'},
  packages = find_packages(),
  tests_require = {'Nose':'nose>=0.1'},
  test_suite = "nose.collector",
  author = 'Cloud Carpenters LLC',
  author_email = 'support@cloudcarpenters.com',
)
