# * This file is part of the MOOSE framework
# * https://www.mooseframework.org
# *
# * All rights reserved, see COPYRIGHT for full restrictions
# * https://github.com/idaholab/moose/blob/master/COPYRIGHT
# *
# * Licensed under LGPL 2.1, please see LICENSE for details
# * https://www.gnu.org/licenses/lgpl-2.1.html

import copy


class ParameterInfo(object):
    """
    Holds the information for a parameter
    """

    def __init__(self, parent, name):
        self._value = ""
        self.user_added = False
        self.name = name
        self.required = False
        self.cpp_type = "string"
        self.basic_type = "String"
        self.group_name = "Main"
        self.description = ""
        self.default = ""
        self.parent = parent
        self.comments = ""
        self.options = []
        self.set_in_input_file = False

    def setFromData(self, data):
        """
        Sets this attributes from a Json dict.
        Input:
            data[dict]: This is the dict description of the parameter as read from the JSON dump.
        """

        self.cpp_type = data["cpp_type"]
        self.basic_type = data["basic_type"]
        self.description = data["description"]
        self.group_name = data["group_name"]
        if not self.group_name:
            self.group_name = "Main"
        self.required = data["required"]
        self.name = data["name"]
        self.options = data.get("options", "")
        if self.options:
            self.options = self.options.strip().split()
        else:
            self.options = []

        default = data.get("default", "")
        if default is None:
            default = ""
        if self.cpp_type == "bool":
            if default == "0":
                default = "false"
            elif default == "1":
                default = "true"
            elif not default:
                default = "false"

        self.default = self._parse(default)
        self._value = self.default

    def copy(self, parent):
        """
        Copies this ParameterInfo to a new one.
        Input:
            parent[BlockInfo]: Parent of the new ParameterInfo
        Return:
            ParameterInfo: The copied parameter
        """
        new = copy.copy(self)
        new.parent = parent
        new.comments = ""
        return new

    def needsQuotes(self):
        """
        Check whether we need to write out quotes around this parameter value.
        Return:
            bool
        """
        return (
            self.isVectorType()
            or self.user_added
            or ("basic_string" in self.cpp_type and self.name == "value")
            or ("std::string" in self.cpp_type and self.name == "value")
            or self.cpp_type == "FunctionExpression"
            or (
                type(self._value) is str
                and (
                    " " in self._value
                    or ";" in self._value
                    or "=" in self._value
                    or "\n" in self._value
                )
            )
        )

    def isVectorType(self):
        """
        Check whether this is a vector type.
        Return:
            bool
        """
        return self.basic_type.startswith("Array")

    def inputFileValue(self):
        """
        Return the string that should be written to the input file.
        Some values needs single quotes while others do not.
        """
        value = self._value

        if type(value) is list:
            file_value = " ".join([self._fileValue(val) for val in value])
        else:
            file_value = self._fileValue(value)

        if self.needsQuotes() and (file_value or self.user_added):
            file_value = "'%s'" % file_value

        return file_value

    def _fileValue(self, value):
        if type(value) is bool:
            if value:
                return "true"
            else:
                return "false"
        else:
            return str(value)

    def hitType(self):
        """
        Return the Hit Field type
        """
        hit_map = {"Boolean": "Bool", "Real": "Float", "Integer": "Int"}
        return hit_map.get(self.basic_type, "String")

    def toolTip(self):
        return self.description + ". Default: %s" % self.default

    def setValue(self, value):
        self._value = self._parse(value)

    def getValue(self):
        return self._value

    def _parse(self, value):
        if value == "" or value is None:
            return ""

        basic_type = self.basic_type
        basic_type_parse_map = {
            "Integer": int,
            "Real": float,
            "Boolean": lambda x: (type(x) is bool and x) or x == "true",
            "String": lambda x: x,
        }

        if basic_type.startswith("Array:"):
            basic_type = basic_type.split("Array:")[-1]
            parse_func = basic_type_parse_map[basic_type]

            if type(value) is str:
                return [parse_func(val) for val in value.split()]
            elif type(value) is list:
                return [parse_func(val) for val in value]
            else:
                return parse_func(value)
        else:
            parse_func = basic_type_parse_map[basic_type]
            return parse_func(value)

    def hasChanged(self):
        return self._value != self.default or self.comments

    def dump(self, o, indent=0, sep="  "):
        o.write("%sName: %s\n" % (indent * sep, self.name))
        o.write("%sValue: %s\n" % (indent * sep, self._value))
        o.write("%sDefault: %s\n" % (indent * sep, self.default))
        o.write("%sUser added: %s\n" % (indent * sep, self.user_added))
        o.write("%sRequired: %s\n" % (indent * sep, self.required))
        o.write("%sCpp_type: %s\n" % (indent * sep, self.cpp_type))
        o.write("%sGroup: %s\n" % (indent * sep, self.group_name))
        o.write("%sDescription: %s\n" % (indent * sep, self.description))
        o.write("%sComments: %s\n" % (indent * sep, self.comments))
