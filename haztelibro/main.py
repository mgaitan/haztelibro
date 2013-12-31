import os
import urllib
import tempfile
from BeautifulSoup import BeautifulSoup
from readability import readability
from utils import dump_to_file
from epubfactory import EpubFactory

def get_readable_html(url, htmlfile=None):
    """given an url, return the local path to a readable version"""
    html = urllib.urlopen(url).read()
    sanitized_html = BeautifulSoup(html).prettify()  # detect encoding
    readable = readability.Document(sanitized_html)
    body = readable.summary()
    html = u"""
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        </head>
        <body>
            %(body)s
        </body>
        <html>
        """  % {'body': body}
    return dump_to_file(BeautifulSoup(html).prettify(), htmlfile)


def urls2epub(input_file, out_file=None, title='Demo', creator='pycamp 2012', language='es_ES'):
    """
    receive a text file of urls (one per line) and convert them to an epub
    """
    htmls = []
    idx = 1
    tmp = tempfile.mkdtemp()
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            print '** processing %s' % line
            htmls.append(get_readable_html(line,
                         os.path.join(tmp, 'Capitulo_%d.html' % idx)))
            idx += 1
    epf = EpubFactory(title, creator, language)
    epf.make_epub(htmls)
    import ipdb; ipdb.set_trace()
    if not out_file:
        out_file = title.replace(' ', '_')
    epf.create_archive(out_file)
    print 'Ok! Epub generado en %s' % out_file

if __name__ == '__main__':
    import sys
    args_len = len(sys.argv)
    if args_len < 2:
        sys.exit('give me an input file')
    elif args_len == 2:
        urls2epub(sys.argv[1])
    elif args_len == 3:
        urls2epub(sys.argv[1], sys.argv[2])
