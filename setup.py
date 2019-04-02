from setuptools import setup


setup(name="metis",
      version="0.0.2",
      description="A toolkit for managing a notebook environment",
      author="Jin Yeom",
      author_email="jin.yeom@hudl.com",
      scripts=["metis"],
      install_requires=["fire", "nbformat"])
