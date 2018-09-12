from setuptools import setup


setup(name="leuchtturm",
      version="0.0.1",
      description="A toolkit for managing a notebook environment",
      author="Jin Yeom",
      author_email="jinyeom@utexas.edu",
      scripts=["leuchtturm"],
      install_requires=["fire", "nbformat"])
