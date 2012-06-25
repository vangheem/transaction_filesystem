import unittest
from transaction_filesystem import tfs
import tempfile
import os
from os import makedirs
import transaction


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        transaction.begin()
        self.fs = tfs()

    def test_rm(self):
        _dir = tempfile.mkdtemp()
        assert os.path.exists(_dir)
        self.fs.rm(_dir)
        transaction.commit()
        assert not os.path.exists(_dir)

    def test_rm_abort(self):
        _dir = tempfile.mkdtemp()
        self.fs.rm(_dir)
        assert not os.path.exists(_dir)
        transaction.abort()
        assert os.path.exists(_dir)

    def test_mkdir(self):
        _dir = tempfile.mkdtemp()
        newdir = os.path.join(_dir, 'foobar')
        self.fs.mkdir(newdir)
        transaction.commit()
        assert os.path.exists(newdir)

    def test_mkdir_abort(self):
        _dir = tempfile.mkdtemp()
        newdir = os.path.join(_dir, 'foobar')
        self.fs.mkdir(newdir)
        transaction.abort()
        assert not os.path.exists(newdir)

    def test_mv(self):
        _dir = tempfile.mkdtemp()
        srcdir = os.path.join(_dir, 'src')
        makedirs(srcdir)
        dstdir = os.path.join(_dir, 'dst')
        self.fs.mv(srcdir, dstdir)
        transaction.commit()
        assert os.path.exists(dstdir)
        assert not os.path.exists(srcdir)

    def test_mv_abort(self):
        _dir = tempfile.mkdtemp()
        srcdir = os.path.join(_dir, 'src')
        makedirs(srcdir)
        dstdir = os.path.join(_dir, 'dst')
        self.fs.mv(srcdir, dstdir)
        assert os.path.exists(dstdir)
        transaction.abort()
        assert not os.path.exists(dstdir)
        assert os.path.exists(srcdir)

    def test_open(self):
        _dir = tempfile.mkdtemp()
        filepath = os.path.join(_dir, 'foo.txt')
        fi = self.fs.open(filepath, 'w')
        fi.write('foobar')
        fi.close()
        transaction.commit()
        assert open(filepath).read() == 'foobar'

    def test_open_abort(self):
        _dir = tempfile.mkdtemp()
        filepath = os.path.join(_dir, 'foo.txt')
        fi = self.fs.open(filepath, 'w')
        fi.write('foobar')
        fi.close()
        transaction.abort()
        assert not os.path.exists(filepath)

    def test_commit_cleans_up_work_dir(self):
        _dir = tempfile.mkdtemp()
        filepath = os.path.join(_dir, 'foo.txt')
        fi = self.fs.open(filepath, 'w')
        fi.write('foobar')
        fi.close()
        assert os.path.exists(self.fs._base_dir)
        transaction.commit()
        assert os.path.exists(self.fs._base_dir)

    def test_multiple_actions(self):
        _dir = tempfile.mkdtemp()
        onedir = os.path.join(_dir, 'one')
        makedirs(onedir)
        twodir = os.path.join(_dir, 'two')
        self.fs.mv(onedir, twodir)
        filepath = os.path.join(twodir, 'foo.txt')
        fi = self.fs.open(filepath, 'w')
        fi.write('blah')
        fi.close()
        filepathtwo = os.path.join(twodir, 'foo2.txt')
        self.fs.mv(filepath, filepathtwo)
        self.fs.rm(twodir)

        transaction.abort()
        assert not os.path.exists(filepath)
        assert not os.path.exists(twodir)
        assert os.path.exists(onedir)


if __name__ == '__main__':
    unittest.main()
