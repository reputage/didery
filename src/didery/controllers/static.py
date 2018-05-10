# ================================================== #
#                     DASHBOARD                      #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/04/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

from __future__ import generator_stop
import falcon
import mimetypes
import os

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class StaticSink(object):
    """
    Class for Falcon sink endpoint serving static files.
    """
    def __init__(self, *pa, **kwa):
        super().__init__(*pa, **kwa)
        self.projectDirpath = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(
                        os.path.expanduser(__file__))))
        self.staticDirpath = os.path.join(self.projectDirpath, "static")

    def __call__(self, req, rep):
        path = req.path
        splits = path.split("/")[1:]
        if not splits[0]:
            splits = splits[1:]
        if splits and splits[0] == "static":
            splits = splits[1:]
        if not splits:
            filepath = "main.html"
        else:
            filepath = "/".join(splits)
        filepath = os.path.join(self.staticDirpath, filepath)
        if not os.path.exists(filepath):
            raise falcon.HTTPError(falcon.HTTP_NOT_FOUND,
                            'Missing Resource',
                            'File "{}" not found or forbidden'.format(filepath))
        filetype = mimetypes.guess_type(filepath, strict=True)[0]
        rep.set_header("Content-Type", "{}; charset=UTF-8".format(filetype))
        rep.status = falcon.HTTP_200
        with open(filepath, 'rb') as f:
            rep.body = f.read()

# ================================================== #
#                        EOF                         #
# ================================================== #