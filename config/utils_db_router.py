import threading

_db_ctx = threading.local()

def set_db(db_name):
    _db_ctx.db = db_name

def get_db():
    return getattr(_db_ctx, 'db', 'default')

class DynamicDbRouter:
    def db_for_read(self, model, **hints):
        return get_db()

    def db_for_write(self, model, **hints):
        return get_db()

    def allow_relation(self, obj1, obj2, **hints):
        db_list = ('default', 'mstcnl')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
