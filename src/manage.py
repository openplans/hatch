#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visionlouisville.settings")

    from django.core.management import execute_from_command_line

    # import pdb; pdb.set_trace()
    execute_from_command_line(sys.argv)
