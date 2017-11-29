# -*- coding: utf-8 -*-

class ModelGroupMeta(type):
    
    def __init__(cls, clsname, bases, attrs):
        super(ModelGroupMeta, cls).__init__(clsname, bases, attrs)
        
        attr_meta = attrs.pop('Meta', None)
        if attr_meta:
            base_cls = attr_meta.BASE_MODEL
            cls._columns = {}
            
            for model_cls in attr_meta.MODELS:
                for field in model_cls._meta.fields:
                    cls._columns[field.name] = model_cls
            for field in base_cls._meta.fields:
                cls._columns[field.name] = base_cls

class ModelGroupBase:
    __metaclass__ = ModelGroupMeta
    
    def __init__(self, model_list=None):
        self.__dict__['_ModelGroupBase__models'] = {}
        if model_list:
            for model in model_list:
                self.setModel(model)
    
    def setModel(self, model):
        model_name = model.__class__.__name__
        self.__models[model_name] = model
    def getModel(self, model_cls):
        return self.__models.get(model_cls.__name__, None)
    
    def __getattr__(self, name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            model_cls = self._columns.get(name)
            if model_cls is None:
                raise AttributeError('%s instance do not have %s' % (self.__class__, name))
            model = self.getModel(model_cls)
            if model is None:
                raise AttributeError('%s instance has not load %s' % (self.__class__, model_cls.__name__))
            return getattr(model, name)
    
    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            self.__dict__[name] = value
        else:
            model_cls = self._columns.get(name)
            if model_cls is None:
                raise AttributeError('%s instance do not have %s' % (self.__class__, name))
            model = self.getModel(model_cls)
            if model is None:
                raise AttributeError('%s instance has not load %s' % (self.__class__, model_cls.__name__))
            setattr(model, name, value)
