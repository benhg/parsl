"""Define the File Type.

The primary purpose of the File object is to track the protocol to be used
to transfer the file as well as to give the appropriate filepath depending
on where (client-side, remote-side, intermediary-side) the File.filepath is
being called from.
"""

import os
import typeguard
import logging
from typing import Dict, Optional
from urllib.parse import urlparse

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from parsl.app.futures import DataFuture


logger = logging.getLogger(__name__)


class File(object):
    """The Parsl File Class.

    This class captures various attributes of a file, and relies on client-side and
    worker-side systems to enable to appropriate transfer of files.

    Note that an error will be raised if one tries to create a File without an
    associated DataManager. That DataManager may be specified explicitly
    as a parameter to the File constructor, or may be implicitly specified via
    a previously loaded Parsl config.

    A File which is not associated with a DataManager is ill-defined.

    """

    @typeguard.typechecked
    def __init__(self, url: str):
        """Construct a File object from a url string.

        Args:
           - url (string) : url string of the file e.g.
              - 'input.txt'
              - 'file:///scratch/proj101/input.txt'
              - 'globus://go#ep1/~/data/input.txt'
              - 'globus://ddb59aef-6d04-11e5-ba46-22000b92c6ec/home/johndoe/data/input.txt'
        """
        self.url = url
        parsed_url = urlparse(self.url)
        self.scheme = parsed_url.scheme if parsed_url.scheme else 'file'
        self.netloc = parsed_url.netloc
        self.path = parsed_url.path
        self.filename = os.path.basename(self.path)

    def __str__(self):
        logger.debug("File with URI {} providing string repr: {}".format(self.url, self.filepath))
        return self.filepath

    def __repr__(self):
        return self.__str__()

    def __fspath__(self):
        return self.filepath

    def is_remote(self):
        if self.scheme in ['ftp', 'http', 'https', 'globus']:
            return True
        elif self.scheme in ['file']:  # TODO: is this enough?
            return False
        else:
            raise Exception('Cannot determine if unknown file scheme {} is remote'.format(self.scheme))

    @property
    def filepath(self):
        """Return the resolved filepath on the side where it is called from.

        The appropriate filepath will be returned when called from within
        an app running remotely as well as regular python on the client side.

        Args:
            - self
        Returns:
             - filepath (string)
        """
        if hasattr(self, 'local_path'):
            return self.local_path

        if self.scheme in ['ftp', 'http', 'https', 'globus']:
            return self.filename
        elif self.scheme in ['file']:
            return self.path
        else:
            raise Exception('Cannot return filepath for unknown scheme {}'.format(self.scheme))


if __name__ == '__main__':

    x = File('./files.py')
