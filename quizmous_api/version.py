from json import load

def get_api_version():
    with open('/usr/local/api/version.json', 'r') as version_file:
        return load(version_file)
