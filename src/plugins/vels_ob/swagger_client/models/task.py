# coding: utf-8

"""
    HDL Testing Platform

    REST API for HDL TP  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class Task(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'user_id': 'str',
        'hdl_file': 'str',
        'design': 'str',
        'pblock': 'int',
        'peripherals': 'list[str]',
        'pins': 'list[Pin]'
    }

    attribute_map = {
        'user_id': 'user_id',
        'hdl_file': 'hdl_file',
        'design': 'design',
        'pblock': 'pblock',
        'peripherals': 'peripherals',
        'pins': 'pins'
    }

    def __init__(self, user_id=None, hdl_file=None, design=None, pblock=None, peripherals=None, pins=None):  # noqa: E501
        """Task - a model defined in Swagger"""  # noqa: E501

        self._user_id = None
        self._hdl_file = None
        self._design = None
        self._pblock = None
        self._peripherals = None
        self._pins = None
        self.discriminator = None

        self.user_id = user_id
        if hdl_file is not None:
            self.hdl_file = hdl_file
        if design is not None:
            self.design = design
        if pblock is not None:
            self.pblock = pblock
        if peripherals is not None:
            self.peripherals = peripherals
        if pins is not None:
            self.pins = pins

    @property
    def user_id(self):
        """Gets the user_id of this Task.  # noqa: E501

        user Identifier  # noqa: E501

        :return: The user_id of this Task.  # noqa: E501
        :rtype: str
        """
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        """Sets the user_id of this Task.

        user Identifier  # noqa: E501

        :param user_id: The user_id of this Task.  # noqa: E501
        :type: str
        """
        if user_id is None:
            raise ValueError("Invalid value for `user_id`, must not be `None`")  # noqa: E501

        self._user_id = user_id

    @property
    def hdl_file(self):
        """Gets the hdl_file of this Task.  # noqa: E501

        uploaded hdl file name  # noqa: E501

        :return: The hdl_file of this Task.  # noqa: E501
        :rtype: str
        """
        return self._hdl_file

    @hdl_file.setter
    def hdl_file(self, hdl_file):
        """Sets the hdl_file of this Task.

        uploaded hdl file name  # noqa: E501

        :param hdl_file: The hdl_file of this Task.  # noqa: E501
        :type: str
        """

        self._hdl_file = hdl_file

    @property
    def design(self):
        """Gets the design of this Task.  # noqa: E501

        design  # noqa: E501

        :return: The design of this Task.  # noqa: E501
        :rtype: str
        """
        return self._design

    @design.setter
    def design(self, design):
        """Sets the design of this Task.

        design  # noqa: E501

        :param design: The design of this Task.  # noqa: E501
        :type: str
        """

        self._design = design

    @property
    def pblock(self):
        """Gets the pblock of this Task.  # noqa: E501

        pblock  # noqa: E501

        :return: The pblock of this Task.  # noqa: E501
        :rtype: int
        """
        return self._pblock

    @pblock.setter
    def pblock(self, pblock):
        """Sets the pblock of this Task.

        pblock  # noqa: E501

        :param pblock: The pblock of this Task.  # noqa: E501
        :type: int
        """

        self._pblock = pblock

    @property
    def peripherals(self):
        """Gets the peripherals of this Task.  # noqa: E501


        :return: The peripherals of this Task.  # noqa: E501
        :rtype: list[str]
        """
        return self._peripherals

    @peripherals.setter
    def peripherals(self, peripherals):
        """Sets the peripherals of this Task.


        :param peripherals: The peripherals of this Task.  # noqa: E501
        :type: list[str]
        """

        self._peripherals = peripherals

    @property
    def pins(self):
        """Gets the pins of this Task.  # noqa: E501


        :return: The pins of this Task.  # noqa: E501
        :rtype: list[Pin]
        """
        return self._pins

    @pins.setter
    def pins(self, pins):
        """Sets the pins of this Task.


        :param pins: The pins of this Task.  # noqa: E501
        :type: list[Pin]
        """

        self._pins = pins

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Task, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Task):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
