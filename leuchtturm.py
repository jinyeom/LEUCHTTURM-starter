#!/usr/bin/env python

import os
import logging
import json
from shutil import rmtree
from copy import deepcopy
from typing import Sequence

import fire
import nbformat


RC_FILENAME = ".ltrc.json"
LT_LOGO = """<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="292px" height="428px" version="1.1" content="&lt;mxfile userAgent=&quot;Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36&quot; version=&quot;9.1.0&quot; editor=&quot;www.draw.io&quot; type=&quot;device&quot;&gt;&lt;diagram id=&quot;c8f287dc-f202-0129-1897-4a35f5549fc9&quot; name=&quot;Page-1&quot;&gt;xVVNc4IwEP013EmiFI+Var305KHnFFbIGAgTo0B/fRNI+Kg6o9M6JjNM9r3dJLtvAY9Eef0uaZl9iAS4h/2k9sibh/ECz/XTAE0HhGHQAalkSQehAdiyb7Cgb9EjS+AwcVRCcMXKKRiLooBYTTAqpaimbjvBp6eWNIUzYBtTfo5+skRlNou5P+AbYGnmTka+Zb5ovE+lOBb2PA+TXTs6OqduL+t/yGgiqhFEVh6JpBCqW+V1BNyU1pWti1tfYft7SyjULQG4CzhRfgR34/ZeqnG1aLMB4488sqwypmBb0tiwlRZfY5nKuaUPSoo9RIIL2UYTvx0946qJdKbLHeN85NoNg4tCrWnOuOmeDfATKBZTS9hmQYG2KWdpoY1YZwvSADK2/Iu2bG4gFdRX64P6qutmBpGDko12sQHYCdv8squhLXBosWzUEjPnSG0rpv3egxx6YRW5rM7sHnX8x6qzCsz8kzoP0IPgG/VAwT/oQZ6kR3guB3o189lyzMhUDrS4IMeltwPfr4Y2h+9iy43+PWT1Aw==&lt;/diagram&gt;&lt;/mxfile&gt;"><defs/><g transform="translate(0.5,0.5)"><rect x="6" y="14" width="280" height="400" rx="19.6" ry="19.6" fill="#333333" stroke="#000000" stroke-width="12" pointer-events="none"/><rect x="6" y="134" width="280" height="160" fill="#e6e6e6" stroke="#000000" stroke-width="12" pointer-events="none"/><rect x="236" y="4" width="20" height="420" fill="#1a1a1a" stroke="#000000" stroke-width="8" pointer-events="none"/></g></svg>"""


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RuntimeConfig(object):
    def __init__(self, rc):
        self.name = rc["name"]
        self.author = rc["author"]
        self.author_email = rc["author_email"]
        self.author_github_id = rc["author_github_id"]
        self.contents = sorted(rc["contents"])

    @classmethod
    def empty(cls):
        return cls(dict(name="LEUCHTTURM",
                        author="Author Name",
                        author_email="author@email.com",
                        author_github_id="",
                        contents=[]))

    def export(self, path):
        data = dict(name=self.name, 
                    author=self.author,
                    author_email=self.author_email,
                    author_github_id=self.author_github_id,
                    contents=self.contents)
        with open(path, "w+") as f:
            f.write(json.dumps(data, indent=4))


class Leuchtturm(object):
    def __init__(self):
        # NOTE: `Leuchtturm` instance is initialized each time the command is called
        # this means that each time the command is called, the current directory is
        # set during initialization
        self._cwd = os.getcwd()
        self._rc_path = os.path.join(self._cwd, RC_FILENAME)

        # if the current directory already has an `rc` file, load it;
        # create an empty one otherwise
        if os.path.exists(self._rc_path):
            with open(self._rc_path, "r") as f:
                self._rc = RuntimeConfig(json.load(f))
        else:
            self._rc = RuntimeConfig.empty()
        
    def _generate_nb(self, nb_dir):
        r"""Generate a new Jupyter notebook"""
        title = os.path.basename(nb_dir) # base name of the directory is always the title
        tmpl = (f"# {title}\n"
                f"Author: {self._rc.author} ({self._rc.author_email})")
        nb_path = os.path.join(nb_dir, title + ".ipynb")
        nb = nbformat.v4.new_notebook()
        nb["cells"] = [nbformat.v4.new_markdown_cell(tmpl),
                       nbformat.v4.new_code_cell()]
        nbformat.write(nb, nb_path)

    def config(self, author=None, author_email=None, author_github_id=None): 
        if author is not None:
            self._rc.author = str(author)
        if author_email is not None:
            # TODO: check if the argument email is really an email
            self._rc.author_email = str(author_email)
        if author_github_id is not None:
            # TODO: this is temporary
            # this functionality should be a little more sophisticated, e.g.,
            # instead of simply adding a github ID, we'll make the user authorize
            # via a proper API for Github
            self._rc.author_github_id = str(author_github_id)
        self._rc.export(self._rc_path)

    def nbviewer_link(self, nb_name):
        converted = nb_name.replace(" ", "%20")
        return (f"https://nbviewer.jupyter.org/github/{self._rc.author_github_id}/"
                f"{self._rc.name}/blob/master/{converted}/{converted}.ipynb")

    def readme(self):
        r"""Generate a new `README.md` file from the list of contents"""
        logo_path = os.path.join(self._cwd, "LEUCHTTURM.svg")
        if not os.path.exists(logo_path):
            with open(logo_path, "w+") as f:
                f.write(LT_LOGO)
        readme_path = os.path.join(self._cwd, "README.md")
        if os.path.exists(readme_path):
            if input("README.md already exists. Overwrite? [y/n]: ").lower() == "n":
                # if the answer is `no`, do nothing and return
                return
        # otherwise, create a new `README.md` and write
        with open(readme_path, "w+") as f:
            contents = "\n".join([f"- [{c}]({self.nbviewer_link(c)})" for c in self._rc.contents])
            f.write(f"<img src=\"LEUCHTTURM.svg\" align=right width=10%></img>\n"
                    f"# {self._rc.name}\n"
                    f"Author: {self._rc.author} ({self._rc.author_email})\n"
                    f"\n"
                    f"## Contents\n"
                    f"{contents}")

    def create(self, nb_name):
        nb_dir = os.path.join(self._cwd, nb_name)
        try:
            os.mkdir(nb_dir) # may raise `FileExistsError`
            self._generate_nb(nb_dir)
        except FileExistsError:
            logger.error(f"'{nb_dir}' already exists")
            return

        # append the new notebook to the contents
        self._rc.contents.append(nb_name)
        self._rc.export(self._rc_path)

    def remove(self, nb_name):
        if nb_name in self._rc.contents:
            if input(f"Remove {nb_name}? [y/n]: ").lower() == "y":
                rmtree(os.path.join(self._cwd, nb_name))
                self._rc.contents.remove(nb_name)
                self._rc.export(self._rc_path)
        else:
            logger.error(f"'{nb_name}' doesn't exist")


if __name__ == "__main__":
    fire.Fire(Leuchtturm)

