import ConfigParser
import os

basepath = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser.RawConfigParser()
config.read(os.path.join(basepath,'aws.conf'))

aws_config = dict(config.items('aws'))
crypt_config = dict(config.items('crypt'))
