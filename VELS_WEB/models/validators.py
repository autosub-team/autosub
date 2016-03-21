# -*- coding: utf-8 -*-

class IS_EMAIL_LIST(object):
    def __init__(self, error_message="Email %s is invalid", sep=","):
        self.error_message = error_message
        self.sep = sep

    def __call__(self, value):
            emails = value.strip().split(self.sep)
            for email in emails:
                email = email.strip()
                if IS_EMAIL()(email)[1] != None:
                    return (email, self.error_message % email)
            return (value, None)
        
class IS_EMAIL_MASS(object):
    def __init__(self, error_message="Email %s is invalid", sep="\n"):
        self.error_message = error_message
        self.sep = sep

    def __call__(self, value):
            emails = value.strip().split(self.sep)
            for email in emails:
                emial = email.strip('\r')
                email = email.strip()
                if IS_EMAIL()(email)[1] != None:
                    return (email, self.error_message % email)
            return (value, None)

class ANY(object):
    """
    Verifies if at least ONE validation is valid!
    e.g. ANY(error_message="should not be empty or email",[IS_NOT_EMPTY(),IS_EMAIL()])
    """

    def __init__(self, error_message, *validators):
        self.validators = validators
        self.error_message=error_message

    def __call__(self, value):
        # against each validator do validate
        results = [validator(value)[1] for validator in self.validators]
        # check if all validations are invalid
        if all(results):
            # invalid, so return the first error message
            return (value, self.error_message)
        else:
            # all valid
            return (value, None)
