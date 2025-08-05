# app/repositories/base.py

class SQLAlchemyRepository:
    def __init__(self, model, session):
        self.model = model
        self.session = session

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        return obj
    
    def get(self, id_):
        return self.session.get(self.model, id_)

    def get_all(self):
        return self.session.query(self.model).all()

    def get_by_attribute(self, attr, value):
        return self.session.query(self.model).filter(getattr(self.model, attr) == value).first()

    def get_all_by_attribute(self, attr, value):
        return self.session.query(self.model).filter(getattr(self.model, attr) == value).all()

    def add(self, instance):
        self.session.add(instance)
        self.session.commit()

    def update(self, id_, update_data):
        self.session.commit()

    def delete(self, id_):
        instance = self.get(id_)
        if not instance:
            return False
        self.session.delete(instance)
        self.session.commit()
        return True
