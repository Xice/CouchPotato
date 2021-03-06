from couchpotato import get_session
from couchpotato.api import addApiView
from couchpotato.core.event import addEvent
from couchpotato.core.helpers.variable import md5, getExt
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
from couchpotato.core.settings.model import FileType, File
from couchpotato.environment import Env
from flask.helpers import send_from_directory
import os.path
import urllib2

log = CPLog(__name__)


class FileManager(Plugin):

    def __init__(self):
        addEvent('file.add', self.add)
        addEvent('file.download', self.download)
        addEvent('file.types', self.getTypes)

        addApiView('file.cache/<path:file>', self.showImage)

    def showImage(self, file = ''):

        cache_dir = Env.get('cache_dir')
        filename = file.replace(cache_dir[1:] + '/', '')

        return send_from_directory(cache_dir, filename)

    def download(self, url = '', dest = None, overwrite = False):

        try:
            file = urllib2.urlopen(url)

            if not dest: # to Cache
                dest = os.path.join(Env.get('cache_dir'), '%s.%s' % (md5(url), getExt(url)))

            if overwrite or not os.path.exists(dest):
                log.debug('Writing file to: %s' % dest)
                output = open(dest, 'wb')
                output.write(file.read())
                output.close()
            else:
                log.debug('File already exists: %s' % dest)

            return dest

        except Exception, e:
            log.error('Unable to download file "%s": %s' % (url, e))

        return False

    def add(self, path = '', part = 1, type = (), properties = {}):

        db = get_session()

        f = db.query(File).filter_by(path = path).first()
        if not f:
            f = File()
            db.add(f)

        f.path = path
        f.part = part
        f.type_id = self.getType(type).id

        db.commit()

        db.expunge(f)
        return f

    def getType(self, type):

        db = get_session()

        type, identifier = type

        ft = db.query(FileType).filter_by(identifier = identifier).first()
        if not ft:
            ft = FileType(
                type = type,
                identifier = identifier,
                name = identifier[0].capitalize() + identifier[1:]
            )

            db.add(ft)
            db.commit()

        return ft

    def getTypes(self):

        db = get_session()

        results = db.query(FileType).all()

        types = []
        for type in results:
            temp = type.to_dict()
            types.append(temp)

        return types
