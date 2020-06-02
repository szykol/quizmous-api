from json import load

def get_api_version():
    """Returns api version

    :return: Api version and build number
    :rtype: json
    """
    with open('/usr/local/api/version.json', 'r') as version_file:
        return load(version_file)
