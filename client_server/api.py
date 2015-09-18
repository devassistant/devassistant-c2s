
import json

import devassistant
from devassistant.actions import actions

from client_server import exceptions, settings

class APIFormatter(object):

    @classmethod
    def format_message(cls, message):
        string = str(message)
        if string[-1] != '\n':
            string += '\n'
        return string

    @classmethod
    def format_json(cls, dictionary):
        dictionary['version'] = settings.API_VERSION
        return cls.format_message(json.dumps(dictionary, sort_keys=True))

    @classmethod
    def format_error(cls, reason):
        return cls.format_json({'error': {'reason': str(reason)}})

    @classmethod
    def format_run_ack(cls, run_id):
        return cls.format_json({'run': {'id': run_id}})

    @classmethod
    def format_run_finished(cls, run_id):
        raise NotImplementedError


class APISerializer(object):

    @classmethod
    def serialize_runnable(cls, runnable, prefix, get_icons=False, get_arguments=False, names_only=False):
        rdict = {
            'name': runnable.name,
            'fullname': getattr(runnable, 'fullname', runnable.name), # Actions do not have fullnames yet
            'description': runnable.description,
            'path': prefix + runnable.name,
        }

        if get_icons:
            rdict['icon'] = getattr(runnable, 'icon', None) # Actions do not have icons yet

        if get_arguments:
            rdict['arguments'] = [arg.__dict__ for arg in runnable.args]

        children = DevAssistantAdaptor.get_children(runnable)
        if names_only:
            rdict['children'] = [c.name for c in children]
        else:
            rdict['children'] = [cls.serialize_runnable(c,
                                                        rdict['path'] + '/',
                                                        get_icons=get_icons,
                                                        get_arguments=get_arguments)
                                 for c in children]
        return rdict

    @classmethod
    def serialize_tree_of_runnables(cls, tree):
        raise NotImplementedError

    @classmethod
    def serialize_log(cls, message, level, run_id):
        raise NotImplementedError


class DevAssistantAdaptor(object):

    @classmethod
    def get_children(cls, runnable, visible_only=False):
        '''Returns a list of children for both actions and assistants'''
        try:
            subactions = runnable.get_subactions()
            if visible_only:
                return [a for a in subactions if not a.hidden]
            else:
                return subactions
        except AttributeError:
            return runnable.get_subassistants()

    @classmethod
    def get_runnable_by_path(cls, path):
        candidates = cls.get_top_runnables()

        for segment in path.split('/')[1:]:
            found = False
            for c in candidates:
                if c.name == segment:
                    found = True
                    candidates = cls.get_children(c)
                    break
            if not found:
                raise exceptions.ProcessingError('Invalid path: ' + path)
        return c

    @classmethod
    def get_top_runnables(cls):
        return [a for a in actions.keys() if not a.hidden] + \
                devassistant.bin.TopAssistant().get_subassistants()

