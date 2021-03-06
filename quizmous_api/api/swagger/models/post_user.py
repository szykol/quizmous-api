# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from .base_model_ import Model
from .. import util


class PostUser(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, nick: str=None, password: str=None):  # noqa: E501
        """PostUser - a model defined in Swagger

        :param nick: The nick of this PostUser.  # noqa: E501
        :type nick: str
        :param password: The password of this PostUser.  # noqa: E501
        :type password: str
        """
        self.swagger_types = {
            'nick': str,
            'password': str
        }

        self.attribute_map = {
            'nick': 'nick',
            'password': 'password'
        }

        self._nick = nick
        self._password = password

    @classmethod
    def from_dict(cls, dikt) -> 'PostUser':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The PostUser of this PostUser.  # noqa: E501
        :rtype: PostUser
        """
        return util.deserialize_model(dikt, cls)

    @property
    def nick(self) -> str:
        """Gets the nick of this PostUser.


        :return: The nick of this PostUser.
        :rtype: str
        """
        return self._nick

    @nick.setter
    def nick(self, nick: str):
        """Sets the nick of this PostUser.


        :param nick: The nick of this PostUser.
        :type nick: str
        """

        self._nick = nick

    @property
    def password(self) -> str:
        """Gets the password of this PostUser.

        This has to be hashed  # noqa: E501

        :return: The password of this PostUser.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password: str):
        """Sets the password of this PostUser.

        This has to be hashed  # noqa: E501

        :param password: The password of this PostUser.
        :type password: str
        """

        self._password = password
