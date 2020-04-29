# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from .base_model_ import Model
from .. import util


class InlineResponse200(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, taken: bool=None):  # noqa: E501
        """InlineResponse200 - a model defined in Swagger

        :param taken: The taken of this InlineResponse200.  # noqa: E501
        :type taken: bool
        """
        self.swagger_types = {
            'taken': bool
        }

        self.attribute_map = {
            'taken': 'taken'
        }

        self._taken = taken

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse200':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200 of this InlineResponse200.  # noqa: E501
        :rtype: InlineResponse200
        """
        return util.deserialize_model(dikt, cls)

    @property
    def taken(self) -> bool:
        """Gets the taken of this InlineResponse200.


        :return: The taken of this InlineResponse200.
        :rtype: bool
        """
        return self._taken

    @taken.setter
    def taken(self, taken: bool):
        """Sets the taken of this InlineResponse200.


        :param taken: The taken of this InlineResponse200.
        :type taken: bool
        """

        self._taken = taken
