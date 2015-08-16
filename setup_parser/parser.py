# coding: utf-8
from __future__ import unicode_literals

import ast

from pkg_resources import Requirement


class SetupParser(object):

    def __init__(self, ast):
        self._ast = ast
        self._setup_call = None

        self.find_setup_call()

    def find_setup_call(self):
        for node in self._ast.body:
            if isinstance(node, ast.Expr) and node.value.func.id == 'setup':
                self._setup_call = node.value
                break

    @staticmethod
    def get_list_values(list_node):
        for value in list_node.value.elts:
            if isinstance(value, ast.Str):
                yield value.s

    def get_requirements(self):
        requirements = []
        if self._setup_call is None:
            return requirements

        keywords = ('install_requires', 'requires', 'tests_require')
        for node in self._setup_call.keywords:
            if node.arg not in keywords:
                continue

            if isinstance(node.value, (ast.List, ast.Tuple)):
                requirements.extend(self.get_list_values(node))

        return requirements


def from_setup_py(file_content):
    ast_code = ast.parse(file_content)

    parser = SetupParser(ast_code)

    found_requirements = []
    for req in parser.get_requirements():
        try:
            found_requirements.append(Requirement.parse(req))
        except ValueError:
            continue

    return found_requirements
