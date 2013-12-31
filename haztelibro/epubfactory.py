# Copyright (C) 2011, Gonzalo Odiard <gonzalo@laptop.org>

import os
import shutil
import zipfile
import BeautifulSoup
import re


class EpubFactory():

    def __init__(self, title, creator, language):
        self._title = title
        self._creator = creator
        # TODO create unique id
        self._id = 'asdfasdfvsadfgsdfhfghfghdfhdfghf'
        self._language = language
        self._cover_image = None

    def make_epub(self, file_list):
        self._tmp_directory = '/tmp'
        self._list_files = file_list

        self.root_directory = self._tmp_directory + "/epub%udir" % os.getpid()
        os.mkdir(self.root_directory)

        self.mimetype_file = self.create_mimetype_file()

        metainf_dir = self.root_directory + '/META-INF'
        os.mkdir(metainf_dir)
        self.create_container_file(metainf_dir)

        oebps_dir = self.root_directory + '/OEBPS'
        os.mkdir(oebps_dir)

        self.create_toc_file(oebps_dir, file_list)

        self.images = []
        self.css = []
        for file_name in file_list:
            if file_name.endswith('.html') or file_name.endswith('.htm'):
                self.clean_html_file(file_name,
                        os.path.join(self.root_directory, 'OEBPS'))
            else:
                shutil.copyfile(file_name,
                    os.path.join(self.root_directory, 'OEBPS',
                    os.path.basename(file_name)))
        """
        if len(self.images) > 0:
            os.mkdir(os.path.join(oebps_dir, 'images'))
        """
        if len(self.css) > 0:
            os.mkdir(os.path.join(oebps_dir, 'css'))

        content_file_list = []
        for file_name in file_list:
            content_file_list.append(os.path.basename(file_name))
        """
        for img_name in self.images:
            shutil.copyfile(img_name,
                os.path.join(self.root_directory, 'OEBPS', 'images',
                os.path.basename(img_name)))
            content_file_list.append(os.path.join('images',
                    os.path.basename(img_name)))
        """
        for css_name in self.css:
            shutil.copyfile(css_name,
                os.path.join(self.root_directory, 'OEBPS', 'css',
                os.path.basename(css_name)))
            content_file_list.append(os.path.join('css',
                    os.path.basename(css_name)))

        self.create_content_file(oebps_dir, content_file_list)

    def create_mimetype_file(self):
        file_name = self.root_directory + "/mimetype"
        fd = open(file_name, 'w')
        fd.write('application/epub+zip')
        fd.close()
        return file_name

    def create_container_file(self, metainf_dir):
        fd = open(metainf_dir + "/container.xml", 'w')
        fd.write('<?xml version="1.0"?>\n')
        fd.write('<container version="1.0" ')
        fd.write('xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n')
        fd.write('<rootfiles>\n')
        fd.write('<rootfile full-path="OEBPS/content.opf" ')
        fd.write('media-type="application/oebps-package+xml" />\n')
        fd.write('</rootfiles>\n')
        fd.write('</container>')
        fd.close()

    def create_content_file(self, oebps_dir, file_list):
        fd = open(oebps_dir + "/content.opf", 'w')

        fd.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fd.write('<package xmlns="http://www.idpf.org/2007/opf" ')
        fd.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        fd.write('unique-identifier="bookid" version="2.0">\n')

        # metadata
        fd.write('<metadata>\n')
        fd.write('<dc:title>%s</dc:title>\n' % self._title)
        fd.write('<dc:creator>%s</dc:creator>\n' % self._creator)
        fd.write('<dc:identifier id="bookid">' +
                'urn:uuid:%s</dc:identifier>\n' % self._id)
        fd.write('<dc:language>%s</dc:language>\n' % self._language)
        fd.write('<meta name="cover" content="%s"/>\n' % self._cover_image)
        fd.write('</metadata>\n')

        # manifest
        fd.write('<manifest>\n')
        fd.write('<item id="ncx" href="toc.ncx" ' +
                'media-type="application/x-dtbncx+xml"/>\n')

        if self._cover_image != None:
            fd.write('<item id="cover" href="title.html" ' +
                    'media-type="application/xhtml+xml"/>\n')

        count = 0
        for file_name in file_list:
            if file_name.endswith('.html') or file_name.endswith('.htm'):
                mime = 'application/xhtml+xml'
            elif file_name.endswith('.css'):
                mime = 'text/css'
            elif file_name.endswith('.png'):
                mime = 'image/png'
            elif file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
                mime = 'image/jpeg'
            elif file_name.endswith('.gif'):
                mime = 'image/gif'
            else:
                mime = ''

            content_id = 'content'
            if count > 0:
                content_id = 'content%d' % count

            fd.write('<item id="%s" href="%s" ' % (content_id, file_name) +
                    'media-type="%s"/>\n' % mime)
            count = count + 1

        if self._cover_image != None:
            fd.write('<item id="cover-image" href="images/cover.png" ' +
                    'media-type="image/png"/>\n')
        fd.write('</manifest>\n')

        # spine
        fd.write('<spine toc="ncx">\n')
        if self._cover_image != None:
            fd.write('<itemref idref="cover" linear="no"/>\n')
        fd.write('<itemref idref="content"/>\n')
        fd.write('</spine>\n')

        # guide
        fd.write('<guide>\n')
        if self._cover_image != None:
            fd.write('<reference href="title.html" type="cover" ' +
                    'title="Cover"/>\n')
        fd.write('</guide>\n')
        fd.write('</package>\n')
        fd.close()

    def create_toc_file(self, oebps_dir, file_list):
        fd = open(oebps_dir + "/toc.ncx", 'w')
        fd.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fd.write('<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"\n')
        fd.write('"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n')
        fd.write('<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" ' +
                'version="2005-1">\n')

        fd.write('<head>\n')
        fd.write('<meta name="dtb:uid" ' +
                'content="urn:uuid:%s"/>\n' % self._id)
        fd.write('<meta name="dtb:depth" content="1"/>\n')
        fd.write('<meta name="dtb:totalPageCount" content="0"/>\n')
        fd.write('<meta name="dtb:maxPageNumber" content="0"/>\n')
        fd.write('</head>\n')

        fd.write('<docTitle>\n')
        fd.write('<text>%s</text>\n' % self._title)
        fd.write('</docTitle>\n')

        fd.write('<navMap>\n')
        np = 1
        if self._cover_image != None:
            fd.write('<navPoint id="navpoint-1" playOrder="1">\n')
            fd.write('<navLabel>\n')
            fd.write('<text>Book cover</text>\n')
            fd.write('</navLabel>\n')
            fd.write('<content src="title.html"/>\n')
            fd.write('</navPoint>\n')
            np = np + 1

        for file_name in file_list:
            fd.write('<navPoint id="navpoint-%d" playOrder="%d">\n' % (np, np))
            fd.write('<navLabel>\n')
            fd.write('<text>Contents</text>\n')
            fd.write('</navLabel>\n')
            fd.write('<content src="%s"/>\n' % os.path.basename(file_name))
            fd.write('</navPoint>\n')
            np = np + 1

        fd.write('</navMap>\n')
        fd.write('</ncx>\n')
        fd.close()

    def create_archive(self, epub_file_name):
        '''Create the ZIP archive.
        The mimetype must be the first file in the archive
        and it must not be compressed.'''

        epub_name = '%s.epub' % epub_file_name

        # The EPUB must contain the META-INF and mimetype files at the root, so
        # we'll create the archive in the working directory first
        # and move it later
        current_cwd = os.getcwd()
        os.chdir(self.root_directory)

        # Open a new zipfile for writing
        epub = zipfile.ZipFile(epub_name, 'w')

        # Add the mimetype file first and set it to be uncompressed
        epub.write('mimetype', compress_type=zipfile.ZIP_STORED)

        # For the remaining paths in the EPUB, add all of their files
        # using normal ZIP compression
        self._scan_dir('.', epub)
        epub.close()
        shutil.move(epub_name, current_cwd)

    def _scan_dir(self, path, epub_file):
        for p in os.listdir(path):
            pp = os.path.join(path, p)
            if os.path.isdir(pp):
                self._scan_dir(pp, epub_file)
            elif p != 'mimetype':
                epub_file.write(os.path.join(path, p),
                            compress_type=zipfile.ZIP_DEFLATED)

    def clean_html_file(self, file_name, dest_directory):
        file_content = open(file_name).read()
        soup = BeautifulSoup.BeautifulSoup(file_content)

        # change src in images and add to the image list
        for img in soup.findAll('img'):
            del(img['border'])

            if not img['src'].startswith('http://'):
                # Same problem again: We flatten layers, so this won't work
                # properly in the wild
                self.images.append(os.path.join(os.path.dirname(file_name),
                        img['src']))
                img['src'] = os.path.join('images',
                        os.path.basename(img['src']))
            else:
                # we need implement this
                pass

        # change href in css links and add to the css list
        for css in soup.findAll('link'):
            if css['rel'] == 'stylesheet':
                if not css['href'].startswith('http://'):
                    self.css.append(os.path.join(
                                os.path.dirname(file_name), css['href']))
                    css['href'] = os.path.join('css',
                            os.path.basename(css['href']))

        # remove all the script nodes
        [item.extract() for item in soup.findAll('script')]

        # remove all the form nodes
        [item.extract() for item in soup.findAll('form')]

        # remove all the cooments
        comments = soup.findAll(text=lambda text: isinstance(text,
                    BeautifulSoup.Comment))
        [comment.extract() for comment in comments]

        # remove links who execute javascript (TODO is not working)
        for link in soup.findAll('a'):
            try:
                if link['href'].startswith('javascript:'):
                    link.extract()
            except:
                pass
            del(link['name'])

        # remove clear in style attribute (TODO is not working)
        for element in soup.find(True):
            try:
                print element
                if element['style'].find('clear') > -1:
                    del(element['style'])
            except:
                pass

        # remove lang property in html node
        for html in soup.findAll('html'):
            del(html['lang'])

        # remove onload property in body node
        for body in soup.findAll('body'):
            del(body['onload'])

        fd = open(os.path.join(dest_directory,
                    os.path.basename(file_name)), 'w')
        fd.write(str(soup))
        fd.close()


if __name__ == '__main__':
    epf = EpubFactory('Historia de la Argentina', 'Gonzalo', 'es_ES')
    epf.make_epub(['datos/NewToolbar.html',
                'datos/essential.shtml.html',
                'datos/essential1.shtml.html'])
    epf.create_archive('/tmp/test-f1')
