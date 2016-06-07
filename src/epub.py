#!C:\Python27\python.exe
# -*- encoding: utf-8 -*-

import zipfile
import os
import shutil
import re
from xml.etree import ElementTree
#from lxml import etree
from gi.repository import GLib

class Chapter:
    def __init__(self, id, href, title=None):
        self.id = id
        self.href = href
        self.title = title

class Epub():
    def __init__(self):
        self.cache_path = GLib.get_user_cache_dir()+\
                          "/gnome-reader/"

        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)
            print(self.cache_path)

        self.name = "" #os.path.basename(file_path)
        self.file_path = ""
        self.opf_path = ""
        self.toc_path = ""
        self.chapters = {}

        self._loaded = False

    def is_loaded(self):
        return self._loaded

    def set_file_path(self, file_path):
        self.file_path = file_path
        self.cache_path+=os.path.basename(file_path)+\
                          "EXTRACTED/"
        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)


    def extract(self):
        shutil.rmtree(self.cache_path)
        zipfile.ZipFile(self.file_path).extractall(path=self.cache_path)


    def prepare(self):
        for event, element in ElementTree.iterparse(self.cache_path+"META-INF/container.xml"):
            if re.search('^rootfile$|}rootfile$', element.tag):
                self.opf_path = self.cache_path+element.attrib['full-path']

        toc_id = ""
        spine = []
        manifest = []
        for event, element in ElementTree.iterparse(self.opf_path):
            if re.search('^spine$|}spine$', element.tag):
            #we get the toc id
                toc_id = element.attrib['toc']
            if re.search('^itemref$|}itemref$', element.tag):
                # we get the spine, wich contains the ordered list of pages id
                spine.append(element.attrib['idref'])
            if re.search('^item$|}item$', element.tag):
                # we get the manifest : all files unordered, their id, their href, their mimetype
                # yay, tuple time ! <(°°<)  ^(°°)^  (>°°)>
                manifest.append((element.attrib['id'], element.attrib['href'], element.attrib['media-type']))

        for count, i in enumerate(spine):
            for item in manifest:
                if item[2] == "application/xhtml+xml":
                    if item[0] == i:
                        self.chapters[int(count)] = Chapter(item[0], os.path.dirname(self.opf_path)+"/"+item[1])
                if item[2] == "application/x-dtbncx+xml":
                    if item[0] == toc_id:
                        self.toc_path = os.path.dirname(self.opf_path)+"/"+item[1]

        navmap = []
        for event, element in ElementTree.iterparse(self.toc_path):
            if re.search('^docTitle$|}docTitle$', element.tag):
                for child in element.getchildren():
                    if re.search('^text$|}text$', child.tag):
                        self.name = child.text

            if re.search('^navPoint$|}navPoint$', element.tag):
                text = ""
                src = ""
                for child in element.getchildren():
                    if re.search('^navLabel$|}navLabel$', child.tag):
                        for grandchild in child.getchildren():
                            if re.search('^text$|}text$', grandchild.tag):
                                text = grandchild.text
                    if re.search('^content$|}content$', child.tag):
                        src = child.attrib['src']
                navmap.append((src, text))

        for i in range(0, len(self.chapters)-1):
            for navpoint in navmap:
                if navpoint[0] in self.chapters[i].href:
                    self.chapters[i].title = navpoint[1]

        self._loaded = True
