import os
import logging
import json
from shutil import rmtree
from copy import deepcopy
from typing import Sequence

import fire
import nbformat


RC_FILENAME = ".leuchtturmrc.json"


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RuntimeConfig(object):
    def __init__(self, rc: dict) -> None:
        self.author = rc["author"]
        self.contents = rc["contents"]

    @classmethod
    def empty(cls):
        return cls(dict(author="", contents=[]))

    def export(self, path):
        data = dict(author=self.author, contents=self.contents)
        with open(path, "w+") as f:
            f.write(json.dumps(data))


class Leuchtturm(object):
    def __init__(self):
        self._cwd = os.getcwd()
        self._rc_path = os.path.join(self._cwd, RC_FILENAME)
        if not os.path.exists(self._rc_path):
            RuntimeConfig.empty().export(self._rc_path)
        with open(self._rc_path, "r") as f:
            self._rc = RuntimeConfig(json.load(f))
        
    def _generate_readme(self) -> None:
        r"""Generate a new `README.md` file from the list of contents"""
        raise NotImplementedError("`_generate_readme` not implemented yet")

    def _generate_nb(self, nb_dir: str) -> None:
        r"""Generate a new Jupyter notebook"""
        title = os.path.basename(nb_dir) # base name of the directory is always the title
        nb_path = os.path.join(nb_dir, title + ".ipynb")
        nb = nbformat.v4.new_notebook()
        nb["cells"] = [nbformat.v4.new_markdown_cell(f"# {title}\n"
                                                     f"Author: {self._rc.author}"),
                       nbformat.v4.new_code_cell()]
        nbformat.write(nb, nb_path)

    def create(self, nb_name: str) -> None:
        cwd = os.getcwd() # current working directory
        nb_dir = os.path.join(cwd, nb_name)
        try:
            os.mkdir(nb_dir) # may raise `FileExistsError`
            self._generate_nb(nb_dir)
        except FileExistsError:
            logger.error(f"{nb_dir} already exists")
            return

        # append the new notebook to the contents
        self._rc.contents.append(nb_name)
        self._rc.export(self._rc_path)

    def remove(self, nb_name: str):
        if nb_name in self._rc.contents:
            resp = input(f"Remove {nb_name}? [y/n]: ")
            if resp.lower() == "y":
                rmtree(os.path.join(self._cwd, nb_name))
                self._rc.contents.remove(nb_name)
                self._rc.export(self._rc_path)
        else:
            logger.error(f"'{nb_name}' doesn't exist")


if __name__ == "__main__":
    fire.Fire(Leuchtturm)

