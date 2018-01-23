#!/usr/bin/python

"""Extension for logging.FileHandler."""

import logging
import os


class ExtFileHandler(logging.FileHandler):
  """Extension class for logging.FileHandler.

  Extends logging.FileHandler with functionality of creating log
  file whether it does not exist.
  """

  def __init__(self, filename, mode="a", encoding=None, delay=0):
    """Inits ExtFileHandler."""
    if not os.path.exists(os.path.dirname(filename)):
      os.makedirs(os.path.dirname(filename))

    if not os.path.exists(filename):
      fd = open(filename, "w")
      fd.close()

    logging.FileHandler.__init__(self, filename, mode, encoding, delay)


def main():
  pass


if __name__ == "__main__":
  main()
