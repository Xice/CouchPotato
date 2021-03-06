from couchpotato.api import addApiView
from couchpotato.core.event import addEvent
from couchpotato.core.helpers.request import getParams, jsonified
from couchpotato.core.logger import CPLog
from couchpotato.core.notifications.base import Notification
from couchpotato.environment import Env
import re
import telnetlib
import urllib
import urllib2

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

log = CPLog(__name__)


class NMJ(Notification):

    def __init__(self):
        addEvent('notify', self.notify)
        addEvent('notify.nmj', self.notify)

        addApiView('notify.nmj.test', self.test)
        addApiView('notify.nmj.auto_config', self.autoConfig)

    def conf(self, attr):
        return Env.setting(attr, 'nmj')

    def autoConfig(self):

        params = getParams()
        host = params.get('host', 'localhost')

        database = ''
        mount = ''

        try:
            terminal = telnetlib.Telnet(host)
        except Exception:
            log.error('Warning: unable to get a telnet session to %s' % (host))
            return self.failed()

        log.debug('Connected to %s via telnet' % (host))
        terminal.read_until('sh-3.00# ')
        terminal.write('cat /tmp/source\n')
        terminal.write('cat /tmp/netshare\n')
        terminal.write('exit\n')
        tnoutput = terminal.read_all()

        match = re.search(r'(.+\.db)\r\n?(.+)(?=sh-3.00# cat /tmp/netshare)', tnoutput)

        if match:
            database = match.group(1)
            device = match.group(2)
            log.info('Found NMJ database %s on device %s' % (database, device))
        else:
            log.error('Could not get current NMJ database on %s, NMJ is probably not running!' % (host))
            return self.failed()

        if device.startswith('NETWORK_SHARE/'):
            match = re.search('.*(?=\r\n?%s)' % (re.escape(device[14:])), tnoutput)

            if match:
                mount = match.group().replace('127.0.0.1', host)
                log.info('Found mounting url on the Popcorn Hour in configuration: %s' % (mount))
            else:
                log.error('Detected a network share on the Popcorn Hour, but could not get the mounting url')
                return self.failed()

        return jsonified({
            'success': True,
            'database': database,
            'mount': mount,
        })

    def notify(self, message = '', data = {}):

        if self.isDisabled():
            return False

        host = self.conf('host')
        mount = self.conf('mount')
        database = self.conf('database')

        if self.mount:
            try:
                req = urllib2.Request(mount)
                log.debug('Try to mount network drive via url: %s' % (mount))
                handle = urllib2.urlopen(req)
            except IOError, e:
                log.error('Warning: Couldn\'t contact popcorn hour on host %s: %s' % (host, e))
                return False

        params = {
            'arg0': 'scanner_start',
            'arg1': database,
            'arg2': 'background',
            'arg3': '',
        }
        params = urllib.urlencode(params)
        UPDATE_URL = 'http://%(host)s:8008/metadata_database?%(params)s'
        updateUrl = UPDATE_URL % {'host': host, 'params': params}

        try:
            req = urllib2.Request(updateUrl)
            log.debug('Sending NMJ scan update command via url: %s' % (updateUrl))
            handle = urllib2.urlopen(req)
            response = handle.read()
        except IOError, e:
            log.error('Warning: Couldn\'t contact Popcorn Hour on host %s: %s' % (host, e))
            return False

        try:
            et = etree.fromstring(response)
            result = et.findtext('returnValue')
        except SyntaxError, e:
            log.error('Unable to parse XML returned from the Popcorn Hour: %s' % (e))
            return False

        if int(result) > 0:
            log.error('Popcorn Hour returned an errorcode: %s' % (result))
            return False
        else:
            log.info('NMJ started background scan')
            return True

    def failed(self):
        return jsonified({'success': False})
