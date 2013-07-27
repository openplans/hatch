"""
This script would be run with the following command:

    cat visions.json | python export_visions.py > data.csv

Where visions.json is the JSON dump of the visions data, and data.csv will be
the resulting CSV file.
"""

import codecs
import cStringIO
import csv
import json
import sys


# Unicode compatible csv writer, from
# http://docs.python.org/2/library/csv.html#csv-examples
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([
            s.encode("utf-8") if isinstance(s, (basestring, unicode)) else s
            for s in row
        ])

        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


data = json.load(sys.stdin)
writer = UnicodeWriter(sys.stdout)
is_header_written = False

for vision in data:
    vision['reply_count'] = len(vision.pop('replies'))
    vision['support_count'] = len(vision.pop('supporters'))
    vision['share_count'] = len(vision.pop('sharers'))

    author_details = vision.pop('author_details')
    for key, value in author_details.items():
        vision['author_' + key] = value

    vision_items = sorted(vision.items())
    if not is_header_written:
        writer.writerow([key for (key, value) in vision_items])
        is_header_written = True

    writer.writerow([value for (key, value) in vision_items])
