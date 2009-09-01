import ConfigParser
try:
    import settings
    conf_path = settings.AWS_CONF_PATH
except:
    conf_path = 'awsapp/aws.conf'
config = ConfigParser.ConfigParser()
config.read(conf_path)
aws_config = dict(config.items('aws'))
crypt_config = dict(config.items('crypt'))
