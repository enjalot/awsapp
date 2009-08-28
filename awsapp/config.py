import ConfigParser
config = ConfigParser.ConfigParser()
config.read("awsapp/aws.conf")
aws_config = dict(config.items('aws'))
crypt_config = dict(config.items('crypt'))
