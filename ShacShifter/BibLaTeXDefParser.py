import logging
import re


class BibLaTeXDefParser:
    """A parser for the BibLaTeX DEF specification."""

    logger = logging.getLogger('ShacShifter.BibLaTeXDefParser')

    def __init__(self):
        # Future node shapes
        self.entryTypes = {}
        # Future property shapes
        self.fields = {}

    def parseDef(self, inputFilePath):
        """Parse the BibLaTeX Specification.

        args: string inputFilePath
        returns: list of dictionaries for entryTypes and entryFields
        """
        with open(inputFilePath, 'r') as file:
            content = file.read()
            reg_match = _RegExLib(content)

            if reg_match.constants:
                pass

            if reg_match.entryTypes:
                for declaration in reg_match.entryTypes:
                    if declaration[0] == '':
                        for entry in [element.strip('\n ') for element in declaration[1].split(',')]:
                            self.entryTypes[entry] = {'skipout': False, 'fields': set()}
                    if declaration[0] == '[skipout]':
                        for entry in [element.strip('\n ') for element in declaration[1].split(',')]:
                            self.entryTypes[entry] = {'skipout': True, 'fields': set()}

            if reg_match.fields:
                # missing options: format, nullok, skipout, label
                fields = set()
                for declaration in reg_match.fields:
                    options = [element.split('=') for element in declaration[0].strip('[]').split(', ')]
                    for entry in [element.strip() for element in declaration[1].split(',')]:
                        for option in options:
                            if option[0] == 'type':
                                fieldType = option[1]
                            if option[0] == 'datatype':
                                dataType = option[1]
                        self.fields[entry] = {'type': fieldType, 'datatype': dataType}

            if reg_match.entryFields:
                for declaration in reg_match.entryFields:
                    if declaration[0] == '':
                        fields = [element.strip('\n ') for element in declaration[1].split(',')]
                        for key, value in self.entryTypes.items():
                            value['fields'].update(fields)
                    else:
                        types = declaration[0].strip('[]').split(',')
                        fields = [element.strip('\n ') for element in declaration[1].split(',')]
                        for key in types:
                            self.entryTypes[key]['fields'].update(fields)

            if reg_match.multiscriptEntryFields:
                # print(reg_match.multiscriptEntryFields)
                pass

            if reg_match.constraints:
                # print(reg_match.constraints)
                # print(re.findall('(.*?)', reg_match.constraints[0]))
                pass

            if False:
                value_type = reg_match.name_score.group(1)
                line = next(file, None)
                while line and line.strip():
                    number, value = line.strip().split(',')
                    value = value.strip()
                    dict_of_data = {
                        'School': school,
                        'Grade': grade,
                        'Student number': number,
                        value_type: value
                    }
                    data.append(dict_of_data)
                    line = next(file, None)

        return 


class _RegExLib:
    """Set up regular expressions"""
    # use https://regexper.com to visualise these if required
    _reg_constants = re.compile(
        r'\\DeclareDatamodelConstant(\[.*?\])?{(.*?)}{(.*?)}', re.DOTALL | re.MULTILINE
    )
    _reg_entryTypes = re.compile(
        r'\\DeclareDatamodelEntrytypes(\[.*?\])?{(.*?)}', re.DOTALL | re.MULTILINE
    )
    _reg_fields = re.compile(
        r'\\DeclareDatamodelFields(\[.*?\])?{(.*?)}', re.DOTALL | re.MULTILINE
    )
    _reg_entryFields = re.compile(
        r'\\DeclareDatamodelEntryfields(\[.*?\])?{(.*?)}', re.DOTALL | re.MULTILINE
    )
    _reg_multiscriptEntryFields = re.compile(
        r'\\DeclareDatamodelMultiscriptEntryfields(\[.*?\])?{(.*?)}', re.DOTALL | re.MULTILINE
    )
    _reg_constraints = re.compile(
        r'\\DeclareDatamodelConstraints(\[.*?\])?{(.*?)}\n\n', re.DOTALL | re.MULTILINE
    )

    __slots__ = [
        'constants',
        'entryTypes',
        'fields',
        'entryFields',
        'multiscriptEntryFields',
        'constraints'
    ]

    def __init__(self, content):
        # check whether line has a positive match with all of the regular expressions
        self.constants = self._reg_constants.findall(content)
        self.entryTypes = self._reg_entryTypes.findall(content)
        self.fields = self._reg_fields.findall(content)
        self.entryFields = self._reg_entryFields.findall(content)
        self.multiscriptEntryFields = self._reg_multiscriptEntryFields.findall(content)
        self.constraints = self._reg_constraints.findall(content)
