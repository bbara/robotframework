#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .tokens import Token


class Settings(object):
    names = ()
    aliases = {}
    multi_use = ()

    def __init__(self):
        self.settings = {n: None for n in self.names}

    def lex(self, statement):
        name_token = statement[0]
        name = self._format_name(name_token.value)
        normalized = self._normalize_name(name)
        try:
            self._validate(name, normalized, statement)
        except ValueError as err:
            name_token.type = Token.ERROR
            name_token.error = err.args[0]
        else:
            name_token.type = getattr(Token, normalized.replace(' ', '_'))
            self.settings[normalized] = statement[1:]
        for token in statement[1:]:
            token.type = Token.ARGUMENT

    def _validate(self, name, normalized, statement):
        if normalized not in self.settings:
            raise ValueError("Non-existing setting '%s'." % name)  # TODO: Hints?
        if self.settings[normalized] and normalized not in self.multi_use:
            raise ValueError("Setting '%s' allowed only once." % name)
        if normalized == "RESOURCE" and len(statement) > 2:
            raise ValueError("Setting '%s' accepts only one value." % name)

    def _normalize_name(self, name):
        upper = name.upper()  # TODO: Non-ASCII spaces
        if upper in self.aliases:
            return self.aliases[upper]
        return upper

    def _format_name(self, name):
        return name


class TestCaseFileSettings(Settings):
    # FIXME: Non-ASCII spaces
    names = (
        'DOCUMENTATION',
        'SUITE SETUP',
        'SUITE TEARDOWN',
        'METADATA',
        'TEST SETUP',
        'TEST TEARDOWN',
        'TEST TEMPLATE',
        'TEST TIMEOUT',
        'FORCE TAGS',
        'DEFAULT TAGS',
        'LIBRARY',
        'RESOURCE',
        'VARIABLES'
    )
    aliases = {
        'TASK SETUP': 'TEST SETUP',
        'TASK TEARDOWN': 'TEST TEARDOWN',
        'TASK TEMPLATE': 'TEST TEMPLATE',
        'TASK TIMEOUT': 'TEST TIMEOUT',
    }
    multi_use = (
        'METADATA',
        'LIBRARY',
        'RESOURCE',
        'VARIABLES'
    )


# FIXME: Implementation missing. Need to check what settings are supported.
class InitFileSettings(Settings):
    pass


class ResourceFileSettings(Settings):
    names = (
        'DOCUMENTATION',
        'LIBRARY',
        'RESOURCE',
        'VARIABLES'
    )
    multi_use = (
        'LIBRARY',
        'RESOURCE',
        'VARIABLES'
    )


class TestCaseSettings(Settings):
    names = (
        'DOCUMENTATION',
        'SETUP',
        'TEARDOWN',
        'TEMPLATE',
        'TIMEOUT',
        'TAGS'
    )

    def __init__(self, parent):
        Settings.__init__(self)
        self.parent = parent

    def _format_name(self, name):
        return name[1:-1].strip()

    @property
    def template_set(self):
        test_template = self.settings['TEMPLATE']
        if self._has_override_value(test_template):
            return False
        parent_template = self.parent.settings['TEST TEMPLATE']
        return self._has_value(test_template) or self._has_value(parent_template)

    def _has_override_value(self, template):
        if template is None:
            return False
        return template == [] or template[0].value.upper() == 'NONE'

    def _has_value(self, template):
        return template and template[0].value


class KeywordSettings(Settings):
    names = (
        'DOCUMENTATION',
        'ARGUMENTS',
        'TEARDOWN',
        'TIMEOUT',
        'TAGS',
        'RETURN'
    )

    def _format_name(self, name):
        return name[1:-1].strip()
