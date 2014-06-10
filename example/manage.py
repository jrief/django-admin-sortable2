#!/usr/bin/env python
import os
import sys
import traceback

sys.path.insert(0, os.path.abspath('./../'))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(sys.argv)
    except Exception as exception:
        print(exception.__repr__())
        traceback.print_exc()
        raise exception
