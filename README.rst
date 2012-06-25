Introduction
============

transaction_filesystem is a way to perform actions on a
filesystem(mkdir, open, rm, mv) within a transaction.

How it works
------------

Start the work::

    import transaction
    transaction.begin()
    from transaction_filesystem import tfs
    fs = tfs(transaction.manager)

Or, leave out transaction argument and it'll use it by default::

    from transaction_filesystem import tfs
    fs = tfs(transaction.manager)

Perform actions through api.

mkdir
~~~~~

Keeps record to be able to remove if transaction aborted::

    fs.mkdir('/path/to/foobar')

mv
~~

Keeps record to be able to move back::

    fs.mv('/src', '/dst')


rm
~~

Actually moves it to tmp directory during transaction::

    fs.rm('/path/to/foobar')

open
~~~~

Works just like normal open call::

    fi = fs.open('/path/to/file.txt', 'w')
    fi.write('foobar')
    fi.close()


Transaction statements
----------------------

commit
~~~~~~

leaves changes alone::

    transaction.commit()


abort
~~~~~

Reverts all filesystem changes::

    transaction.abort()


Without formal transaction management::

    fs.commit()

or::

    fs.abort()


Savepoints
----------

rolling back to save point will only after parts::

    sp = transaction.savepoint()
    # do other stuff...
    sp.rollback()
