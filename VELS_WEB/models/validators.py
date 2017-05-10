# -*- coding: utf-8 -*-

from os.path import isfile
from os.path import isdir

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
            lines = value.strip().split(self.sep)
            for line in lines:
		line= line.strip("\r ")
            	elements = line.split(';')
            	email= elements[0].strip()
                if IS_EMAIL()(email)[1] != None:
                    return (email, self.error_message % email)
            return (value, None)

class FILE_EXISTS(object):
    def __init__(self, error_message="File does not exist"):
        self.error_message = error_message

    def __call__(self, value):
        filename = value
        if isfile(filename) == False:
            return(filename, self.error_message)
        else:
            return (filename, None)

class PATH_EXISTS(object):
    def __init__(self, error_message="Path does not exist"):
        self.error_message = error_message

    def __call__(self, value):
        pathname = predir + "/" + value
        if isdir(pathname) == False:
            return(pathname, self.error_message)
        else:
            return (pathname, None)

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
