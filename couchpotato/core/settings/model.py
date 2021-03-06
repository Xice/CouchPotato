from elixir.entity import Entity
from elixir.fields import Field
from elixir.options import options_defaults
from elixir.relationships import OneToMany, ManyToOne
from libs.elixir.options import using_options
from libs.elixir.relationships import ManyToMany
from sqlalchemy.types import Integer, Unicode, UnicodeText, Boolean, Float, \
    String

options_defaults["shortnames"] = True

# We would like to be able to create this schema in a specific database at
# will, so we can test it easily.
# Make elixir not bind to any session to make this possible.
#
# http://elixir.ematia.de/trac/wiki/Recipes/MultipleDatabasesOneMetadata
__session__ = None


class Movie(Entity):
    """Movie Resource a movie could have multiple releases
    The files belonging to the movie object are global for the whole movie
    such as trailers, nfo, thumbnails"""

    last_edit = Field(Integer)

    library = ManyToOne('Library')
    status = ManyToOne('Status')
    profile = ManyToOne('Profile')
    releases = OneToMany('Release')
    files = ManyToMany('File')


class Library(Entity):
    """"""

    year = Field(Integer)
    identifier = Field(String(20))
    rating = Field(Float)

    plot = Field(UnicodeText)
    tagline = Field(UnicodeText(255))

    status = ManyToOne('Status')
    movie = OneToMany('Movie')
    titles = OneToMany('LibraryTitle')
    files = ManyToMany('File')


class LibraryTitle(Entity):
    """"""

    title = Field(Unicode)
    default = Field(Boolean)

    language = OneToMany('Language')
    libraries = ManyToOne('Library')


class Language(Entity):
    """"""

    identifier = Field(String(20))
    label = Field(Unicode)

    titles = ManyToOne('LibraryTitle')


class Release(Entity):
    """Logically groups all files that belong to a certain release, such as
    parts of a movie, subtitles."""

    movie = ManyToOne('Movie')
    status = ManyToOne('Status')
    quality = ManyToOne('Quality')
    files = ManyToMany('File')
    history = OneToMany('History')


class Status(Entity):
    """The status of a release, such as Downloaded, Deleted, Wanted etc"""

    identifier = Field(String(20), unique = True)
    label = Field(Unicode(20))

    releases = OneToMany('Release')
    movies = OneToMany('Movie')


class Quality(Entity):
    """Quality name of a release, DVD, 720P, DVD-Rip etc"""
    using_options(order_by = 'order')

    identifier = Field(String(20), unique = True)
    label = Field(Unicode(20))
    order = Field(Integer)

    size_min = Field(Integer)
    size_max = Field(Integer)

    releases = OneToMany('Release')
    profile_types = OneToMany('ProfileType')


class Profile(Entity):
    """"""
    using_options(order_by = 'order')

    label = Field(Unicode(50))
    order = Field(Integer)
    core = Field(Boolean)
    hide = Field(Boolean)

    movie = OneToMany('Movie')
    types = OneToMany('ProfileType', cascade = 'all, delete-orphan')


class ProfileType(Entity):
    """"""
    using_options(order_by = 'order')

    order = Field(Integer)
    finish = Field(Boolean)
    wait_for = Field(Integer)

    quality = ManyToOne('Quality')
    profile = ManyToOne('Profile')


class File(Entity):
    """File that belongs to a release."""

    path = Field(Unicode(255), nullable = False, unique = True)
    part = Field(Integer, default = 1)

    type = ManyToOne('FileType')
    properties = OneToMany('FileProperty')

    history = OneToMany('RenameHistory')
    movie = ManyToMany('Movie')
    release = ManyToMany('Release')
    library = ManyToMany('Library')


class FileType(Entity):
    """Types could be trailer, subtitle, movie, partial movie etc."""

    identifier = Field(String(20), unique = True)
    type = Field(Unicode(20))
    name = Field(Unicode(50), nullable = False)

    files = OneToMany('File')


class FileProperty(Entity):
    """Properties that can be bound to a file for off-line usage"""

    identifier = Field(String(20))
    value = Field(Unicode(255), nullable = False)

    file = ManyToOne('File')


class History(Entity):
    """History of actions that are connected to a certain release,
    such as, renamed to, downloaded, deleted, download subtitles etc"""

    message = Field(UnicodeText())
    release = ManyToOne('Release')


class RenameHistory(Entity):
    """Remembers from where to where files have been moved."""

    old = Field(Unicode(255))
    new = Field(Unicode(255))

    file = ManyToOne('File')


def setup():
    """ Setup the database and create the tables that don't exists yet """
    from elixir import setup_all, create_all
    from couchpotato import get_engine

    setup_all()
    create_all(get_engine())
