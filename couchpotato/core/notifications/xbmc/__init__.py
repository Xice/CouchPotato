from .main import XBMC

def start():
    return XBMC()

config = [{
    'name': 'xbmc',
    'groups': [
        {
            'tab': 'notifications',
            'name': 'xbmc',
            'options': [
                {
                    'name': 'enabled',
                    'default': 0,
                    'type': 'enabler',
                },
                {
                    'name': 'host',
                    'default': 'localhost:8080',
                },
                {
                    'name': 'username',
                    'default': 'xbmc',
                },
                {
                    'name': 'password',
                    'default': 'xbmc',
                    'type': 'password',
                },
            ],
        }
    ],
}]
