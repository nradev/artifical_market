from mesa.datacollection import DataCollector
from operator import attrgetter

class ModDataCollector(DataCollector):
    def __init__(self, model_reporters=None, agent_reporters=None, tables=None):
        super().__init__(model_reporters, agent_reporters, tables)

    @staticmethod
    def _make_attribute_collector(attr):
        '''
        Create a function which collects the value of a named attribute
        '''
        def attr_collector(obj):
            return attrgetter(attr)(obj)
            #return getattr(obj, attr)

        return attr_collector