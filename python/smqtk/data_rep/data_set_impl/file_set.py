__author__ = 'purg'

import cPickle

import multiprocessing

import os

import re

from smqtk.data_rep import DataElement, DataSet
from smqtk.utils.file_utils import iter_directory_files, partition_string



class FileSet (DataSet):
    """
    File-based data set. Data elements will all be file-based (DataFile type,
    see ``../data_element_impl/file_element.py``).

    File sets are initialized with a root directory, under which it attempts to
    find existing serialized DataElement pickle files. This notion means that
    DataElement implementations stored must be picklable.

    """

    # Filename template for serialized files. Requires template
    SERIAL_FILE_TEMPLATE = "UUID_%s.MD5_%s.dataElement"

    # Regex for matching file names as valid FileSet serialized elements
    # - yields two groups, the first is the UUID, the second is the MD5 sum
    SERIAL_FILE_RE = re.compile("UUID_(\w+).MD5_(\w+).dataElement")

    def __init__(self, root_directory, md5_chunk=8):
        """
        Initialize a new or existing file set from a root directory.

        :param root_directory: Directory that this file set is based in.
        :type root_directory: str

        :param md5_chunk: Number of segments to split data element MD5 sum into
            when saving element serializations.
        :type md5_chunk: int

        """
        self._root_dir = os.path.abspath(root_directory)
        self._md5_chunk = md5_chunk

        #: :type: dict[object, smqtk.data_rep.DataElement]
        self._element_map = {}
        self._element_map_lock = multiprocessing.RLock()

        self._discover_data_elements()

    def __del__(self):
        """
        Serialize out element contents on deletion.
        """
        self._save_data_elements()

    def _discover_data_elements(self):
        """
        From the set root directory, find serialized files, deserialize them and
        store in instance mapping.
        """
        with self._element_map_lock:
            for fpath in iter_directory_files(self._root_dir, True):
                m = self.SERIAL_FILE_RE.match(os.path.basename(fpath))
                if m:
                    with open(fpath) as f:
                        #: :type: smqtk.data_rep.DataElement
                        de = cPickle.load(f)
                    self._element_map[de.uuid()] = de

    def _save_data_elements(self):
        """
        Serialize out data elements in mapping into the root directory.
        """
        with self._element_map_lock:
            for uuid, de in self._element_map.iteritems():
                md5 = de.md5()
                # Leaving off trailing chunk so that we don't have a single
                # directory per md5-sum.
                containing_dir = \
                    os.path.join(self._root_dir,
                                 *partition_string(md5, self._md5_chunk))
                if not os.path.isdir(containing_dir):
                    os.makedirs(containing_dir)

                output_fname = os.path.join(
                    containing_dir,
                    self.SERIAL_FILE_TEMPLATE % (str(uuid), md5)
                )
                with open(output_fname, 'wb') as ofile:
                    cPickle.dump(de, ofile)

    def count(self):
        """
        :return: The number of data elements in this set.
        :rtype: int
        """
        return len(self._element_map)

    def has_uuid(self, uuid):
        """
        Test if the given uuid refers to an element in this data set.

        :param uuid: Unique ID to test for inclusion. This should match the type
            that the set implementation expects or cares about.

        :return: True if the given uuid matches an element in this set, or False
            if it does not.
        :rtype: bool

        """
        with self._element_map_lock:
            return uuid in self._element_map

    def add_data(self, elem):
        """
        Add the given data element instance to this data set.

        :param elem: Data element to add
        :type elem: smqtk.data_rep.DataElement

        """
        assert isinstance(elem, DataElement)
        with self._element_map_lock:
            self._element_map[elem.uuid()] = elem

    def get_data(self, uuid):
        with self._element_map_lock:
            return self._element_map[uuid]
