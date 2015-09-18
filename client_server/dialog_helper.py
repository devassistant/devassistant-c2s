import json

from devassistant.command_helpers import DialogHelper


class JSONDialogHelperMetaClass(type):
    def __copy__(self, memo):
        return self

    def __deepcopy__(self, memo):
        return self


@DialogHelper.register_helper
class JSONDialogHelper(object):
    __metaclass__ = JSONDialogHelperMetaClass

    shortname = 'json'
    yes_list = ['y', 'yes']
    yesno_list = yes_list + ['n', 'no']

    # TODO: solve this in some less smelly way
    handler = None
    run_id = None

    def __copy__(self, memo):
        return self

    def __deepcopy__(self, memo):
        return self

    @classmethod
    def is_available(cls):
        return True

    @classmethod
    def is_graphical(cls):
        return False

    @classmethod
    def ask_for_confirm_with_message(cls, prompt, message, **options):
        prompt += ' [y/n]'
        while True:
            choice = cls.ask_for_input_with_prompt(prompt, message=message, **options)
            choice = choice.lower()
            if choice not in cls.yesno_list:
                cls.handler.send_error('You have to choose one of y/n.')
            else:
                return choice in cls.yes_list

    @classmethod
    def ask_for_package_list_confirm(cls, prompt, package_list, **options):
        prompt += ' [y(es)/n(o)/s(how)]: '
        while True:
            choice = cls.ask_for_input_with_prompt(prompt, **options)
            choice = choice.lower()
            if choice not in cls.yesno_list + ['s', 'show']:
                cls.handler.send_error('You have to choose one of y/n/s.')
            else:
                if choice in cls.yesno_list:
                    return choice in cls.yes_list
                else:
                    print('\n'.join(sorted(package_list)))
                    # TODO log this instead of printing

    @classmethod
    def _ask_for_text_or_password(cls, prompt, type, **options):
        print(options)
        question = {'id': cls.run_id, 'prompt': prompt, 'type': type}
        msg = options.get('message', None)
        if msg:
            question['message'] = msg
        cls.handler.send_message({'question': question})

        while True:
            try:
                reply = yield from cls.handler.get_answer()
                if reply['answer']['id'] != cls.run_id:
                    raise(Exception('Invalid id'))
                inp = reply['answer']['value']
                return inp
            except BaseException as e:
                raise(e)
                cls.handler.send_error(e)

    @classmethod
    def ask_for_input_with_prompt(cls, prompt, **options):
        return cls._ask_for_text_or_password(prompt, 'input_with_prompt', **options)

    @classmethod
    def ask_for_password(cls, prompt, **options):
        return cls._ask_for_text_or_password(prompt, 'password', **options)
