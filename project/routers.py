class Chatrouter:
    """
    a router that sends queries for the chat model to the 'mongo_db' database
    and queries for other models to the 'default' database.
    """

    def db_for_read(self, model, **hints):
        """
        return the database alias for reading operations.
        """
        if model._meta.app_label == 'chat' :
            return 'mongo_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        return the database alias for writing operations.
        """
        if model._meta.app_label == 'chat':
            return 'mongo_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        return true if a relation between obj1 and obj2 is allowed.
        """
        if obj1._meta.app_label == 'chat' and obj2._meta.app_label == 'chat':
            return True
        elif obj1._meta.app_label == 'chat' or obj2._meta.app_label == 'chat':
            return False  # relations between chat models and other models are not allowed
        return None  # use the default behavior for other models

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        return true if migrations are allowed on the given database.
        """
        if app_label == 'chat':
            return db == 'mongo_db'  # migrations for chat models should only run on the 'mongo_db' database
        return None  # use the default behavior for other models
