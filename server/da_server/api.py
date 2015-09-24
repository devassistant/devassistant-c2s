import base64
import hashlib
import json
import mimetypes

import devassistant
from devassistant.actions import actions
from devassistant.logger import logger as dalogger
from devassistant import path_runner

from da_server import exceptions, settings

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
    def format_error(cls, reason, run_id=''):
        error = {'error': {'reason': str(reason)}}
        if run_id:
            error['error']['id'] = run_id
        return cls.format_json(error)

    @classmethod
    def format_run_ack(cls, run_id):
        return cls.format_json({'run': {'id': run_id}})

    @classmethod
    def format_run_finished(cls, run_id, status):
        return cls.format_json({'finished': {'id': run_id, 'status': status}})


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
            rdict['icon'] = cls.serialize_icon(runnable, get_icons)

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
    def serialize_log(cls, message, level, run_id):
        return {"log": {"level": level, "message": message, "id": run_id}}

    @classmethod
    def serialize_icon(cls, assistant, variant):
        if not getattr(assistant, 'icon_path', ''):
            return None
        icon = {'checksum': cls._md5file(assistant.icon_path)}
        if variant == 'data':
            icon['data'] = cls._base64file(assistant.icon_path)
            icon['mimetype'] = cls._mimefile(assistant.icon_path)
        return icon

    @classmethod
    def _md5file(cls, fname):
        """http://stackoverflow.com/a/3431838"""
        hash = hashlib.md5()
        with open(fname, 'rb') as f:
            hash.update(f.read())
        return hash.hexdigest()

    @classmethod
    def _base64file(cls, fname):
        """http://stackoverflow.com/a/3715530"""
        with open(fname, 'rb') as f:
            encoded_string = base64.b64encode(f.read())
        return encoded_string.decode()

    @classmethod
    def _mimefile(cls, fname):
        return mimetypes.guess_type(fname)[0]


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

    @classmethod
    def path_to_dict(cls, path):
        '''Convrets a path (str separated with /) to dict path runner expects'''
        path = path.split('/')[1:]
        ret = {}
        for number in range(len(path)):
            ret['subassistant_{}'.format(number)] = path[number]
        return ret

    @classmethod
    def get_runnable_to_run(cls, path, args):
        try:
            p = devassistant.bin.TopAssistant().get_selected_subassistant_path(
                       **cls.path_to_dict(path))
            to_run = path_runner.PathRunner(p, args)
        except BaseException:
            # this can only be used for actions here!
            to_run = cls.get_runnable_by_path(path)(**args)
        return to_run

    @classmethod
    def get_logger(cls):
        return dalogger
