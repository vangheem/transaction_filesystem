from transaction.interfaces import ISavepointDataManager
from transaction.interfaces import IDataManagerSavepoint
from transaction.interfaces import ISavepoint
from zope.interface import implementer
import transaction
from os import path
from os import makedirs
from os import remove
import tempfile
import errno
from shutil import rmtree
from shutil import move
from shutil import copy2 as copy


@implementer(ISavepointDataManager)
class FSDataManager(object):
    def __init__(self, tfs, manager):
        self.tfs = tfs
        self.transaction_manager = manager

    def abort(self, transaction):
        self.tfs.abort()

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        self.tfs.commit()

    def tpc_abort(self, transaction):
        pass

    def sortKey(self):
        return 0

    def savepoint(self):
        raise NotImplemented()


@implementer(IDataManagerSavepoint)
class FSDataManagerSavepoint(object):
    def __init__(self):
        pass


@implementer(ISavepoint)
class FSSavepoint(object):
    def __init__(self):
        pass


def mkdir_p(pth):
    if path.exists(pth):
        return
    try:
        makedirs(pth)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


class BaseAction(object):
    def __init__(self, workdir, key, path1, path2=None):
        self.workdir = workdir
        self.key = str(key)
        self.path1 = path1
        self.path2 = path2

    @property
    def workpath1(self):
        pth = path.join(self.workdir, self.key, self.path1.strip(path.sep))
        mkdir_p(path.sep.join(pth.split(path.sep)[:-1]))
        return pth

    @property
    def workpath2(self):
        pth = path.join(self.workdir, self.key, self.path2.strip(path.sep))
        mkdir_p(path.sep.join(pth.split(path.sep)[:-1]))
        return pth


class MkdirAction(BaseAction):
    def __call__(self):
        mkdir_p(self.path1)

    def rollback(self):
        rmtree(self.path1)


class MvAction(BaseAction):

    def __call__(self):
        move(self.path1, self.path2)

    def rollback(self):
        if path.exists(self.path1):
            rmtree(self.path1)
        move(self.path2, self.path1)


class RmAction(BaseAction):
    """
    Instead of actually deleting, move to work
    directory so it can be restored
    """

    def __call__(self):
        move(self.path1, self.workpath1)

    def rollback(self):
        move(self.workpath1, self.path1)


class OpenAction(BaseAction):
    """
    On opening a file for write, make copy so it can be
    rolled back
    """

    def __call__(self):
        mode = self.path2
        if path.exists(self.path1):
            # make copy before...
            self.has_existing = True
            copy(self.path1, self.workpath1)
        else:
            self.has_existing = False
        return open(self.path1, mode)

    def rollback(self):
        if self.has_existing:
            copy(self.workpath1, self.path1)
        else:
            if path.exists(self.path1):
                remove(self.path1)


class tfs(object):
    def __init__(self, manager=None):
        if manager is None:
            manager = transaction.manager
        self.dm = FSDataManager(self, manager)
        manager.get().join(self.dm)
        self._base_dir = tempfile.mkdtemp()
        self._action_stack = []

    def abort(self):
        for action in reversed(self._action_stack):
            action.rollback()
            if path.exists(path.join(self._base_dir, action.key)):
                rmtree(path.join(self._base_dir, action.key))
        self._action_stack = []

    def commit(self):
        self._action_stack = []
        rmtree(self._base_dir)
        self._base_dir = tempfile.mkdtemp()

    def _execute_action(self, action, *args):
        action = action(self._base_dir, len(self._action_stack), *args)
        self._action_stack.append(action)
        return action()

    def mkdir(self, pth):
        self._execute_action(MkdirAction, pth)

    def mv(self, pth1, pth2):
        self._execute_action(MvAction, pth1, pth2)

    def rm(self, pth):
        self._execute_action(RmAction, pth)

    def open(self, pth, mode):
        if 'w' in mode or 'a' in mode:
            return self._execute_action(OpenAction, pth, mode)
        else:
            return open(pth, mode)
