import logging
import re


class BibLaTeXDefParser:
    """A parser for the BibLaTeX DEF specification."""

    logger = logging.getLogger('ShacShifter.BibLaTeXDefParser')

    def __init__(self):
        # Future shapes
        self.entryTypes = {}

    def parseDef(self, inputFilePath):
        """Parse the BibLaTeX Specification.

        args: string inputFilePath
        returns: list of dictionaries for entryTypes and entryFields
        """
        with open(inputFilePath, 'r') as file:
            content = file.read()
            reg_match = _RegExLib(content.replace(' ',''))

            fieldsDict = {}
            
            if reg_match.constants:
                # not (yet) relevant
                pass

            if reg_match.entryTypes:
                for declaration in reg_match.entryTypes:
                    if declaration[0] == '':
                        for entry in [element.strip('\n') for element in declaration[1].split(',')]:
                            self.entryTypes[entry] = EntryType(name=entry, skipout=False)
                    if declaration[0] == '[skipout]':
                        for entry in [element.strip('\n') for element in declaration[1].split(',')]:
                            self.entryTypes[entry] = EntryType(name=entry, skipout=True)

            if reg_match.fields:
                # missing options: format, nullok, skipout, label
                for declaration in reg_match.fields:
                    options = [element.split('=') for element in declaration[0].strip('[]').split(',')]
                    for entry in [element.strip() for element in declaration[1].split(',')]:
                        for option in options:
                            if option[0] == 'type':
                                fieldType = option[1]
                            if option[0] == 'datatype':
                                dataType = option[1]
                        fieldsDict[entry] = Field(name=entry, type=fieldType, dataType=dataType)

            if reg_match.entryFields:
                for declaration in reg_match.entryFields:
                    if declaration[0] == '':
                        # for all entryTypes
                        fields = [element.strip('\n') for element in declaration[1].split(',')]
                        for num, field in enumerate(fields):
                            if field not in fieldsDict:
                                fieldsDict[field] = Field(name=field, type=False, dataType=False)
                                fields[num] = fieldsDict[field]
                            else:
                                fields[num] = fieldsDict[field]
                        for key, value in self.entryTypes.items():
                            self.entryTypes[key].fields.extend(fields)
                    else:
                        # for specific entryTypes
                        types = declaration[0].strip('[]').split(',')
                        fields = [element.strip('\n') for element in declaration[1].split(',')]
                        for num, field in enumerate(fields):
                            if field not in fieldsDict:
                                fieldsDict[field] = Field(name=field, type=False, dataType=False)
                                fields[num] = fieldsDict[field]
                            else:
                                fields[num] = fieldsDict[field]
                        for key in types:
                            self.entryTypes[key].fields.extend(fields)

            if reg_match.multiscriptEntryFields:
                # not (yet) relevant
                for declaration in reg_match.multiscriptEntryFields:
                    if declaration[0] == '':
                        # for all entryTypes
                        for entry in [element.strip('\n') for element in declaration[1].split(',')]:
                            pass
                    else:
                        # for specific entryTypes
                        types = declaration[0].strip('[]').split(',')
                        fields = [element.strip('\n') for element in declaration[1].split(',')]
                        for key in types:
                            pass

            if reg_match.constraints:
                # TODO also get fields after xor and or fields, problem: '^}' not safe
                for declaration in reg_match.constraints:
                    constraints = list(filter(None, declaration[1].replace('\n','').split('\\constraint[')))
                    constraints = [element.split(']') for element in constraints]
                    types = [element.strip('\n') for element in declaration[0].strip('[]').split(',')]
                    self.parseConstraints(constraints, types)
        return self.entryTypes

    def parseConstraints(self, constraints, types):
        regField = r'\\constraintfield{(.*?)}'

        for constraint in constraints:
            options = [element.split('=') for element in constraint[0].strip('[]').split(',')]
            constraint = constraint[1][1:-1]
            dataType = rangemin = rangemax = pattern = False
            for option in options:
                if option[0] == 'type':
                    constraintType = option[1]
                if option[0] == 'datatype':
                    dataType = option[1]
                if option[0] == 'rangemin':
                    rangemin = option[1]
                if option[0] == 'rangemax':
                    rangemax = option[1]
                if option[0] == 'pattern':
                    pattern = option[1]
            if constraintType == 'mandatory':
                constraintFields = []
                if '\\constraintfieldsor' in constraint or '\\constraintfieldsxor' in constraint:
                    # or and xor
                    orCon = False
                    if '\\constraintfieldsor'in constraint:
                        orCon = True
                        parts = list(filter(None, constraint.split('\\constraintfieldsor{')))
                    else:
                        parts = list(filter(None, constraint.split('\\constraintfieldsxor{')))
                    for part in parts:
                        if '}}' in part:
                            arr = part.split('}}')
                            arr[0] += '}'
                            orFields = re.findall(regField, arr[0], re.DOTALL | re.MULTILINE)
                            # add or/xor flag
                            if types != ['']:
                                # for specific entryTypes
                                for key in types:
                                    for num, field in enumerate(self.entryTypes[key].fields):
                                        if field.name in orFields:
                                            if orCon:
                                                self.entryTypes[key].fields[num].orConstraint = True
                                            else:
                                                self.entryTypes[key].fields[num].xorConstraint = True
                            else:
                                # for all entryTypes
                                for key, value in self.entryTypes.items():
                                    for num, field in enumerate(self.entryTypes[key].fields):
                                        if field.name in orFields:
                                            if orCon:
                                                self.entryTypes[key].fields[num].orConstraint = True
                                            else:
                                                self.entryTypes[key].fields[num].xorConstraint = True
                            constraintFields.extend(orFields)
                            constraintFields.extend(re.findall(regField, arr[1], re.DOTALL | re.MULTILINE))
                        else:
                            constraintFields.extend(re.findall(regField, part, re.DOTALL | re.MULTILINE))
                else:
                    # only get fields
                    constraintFields.extend(re.findall(regField, constraint, re.DOTALL | re.MULTILINE))
                # add mandatory flag
                if types != ['']:
                    # for specific entryTypes
                    for key in types:
                        for num, field in enumerate(self.entryTypes[key].fields):
                            if field.name in constraintFields:
                                self.entryTypes[key].fields[num].mandatory = True
                else:
                    # for all entryTypes
                    for key, value in self.entryTypes.items():
                        for num, field in enumerate(self.entryTypes[key].fields):
                            if field.name in constraintFields:
                                self.entryTypes[key].fields[num].mandatory = True
            elif constraintType == 'data':
                constraintFields = re.findall(regField, constraint, re.DOTALL | re.MULTILINE)
                if types != ['']:
                    # for specific entryTypes
                    for key in types:
                        for num, field in enumerate(self.entryTypes[key].fields):
                            if field.name in constraintFields:
                                self.entryTypes[key].fields[num].contraints = {
                                    'dataype': dataType,
                                    'rangemin': rangemin,
                                    'rangemax': rangemax,
                                    'pattern': pattern
                                }
                else:
                    # for all entryTypes
                    for key, value in self.entryTypes.items():
                        for num, field in enumerate(self.entryTypes[key].fields):
                            if field.name in constraintFields:
                                self.entryTypes[key].fields[num].contraints = {
                                    'dataype': dataType,
                                    'rangemin': rangemin,
                                    'rangemax': rangemax,
                                    'pattern': pattern
                                }
            elif constraintType == 'conditional':
                pass

class EntryType:
    def __init__(self, name, skipout):
        self.name = name
        self.skipout = skipout
        self.fields = []

    def __str__(self):
        return 'name={}, skipout={}, fields={}'.format(self.name, self.skipout, [field.name for field in self.fields])

class Field:
    def __init__(self, name, type=False, dataType=False):
        self.name = name
        self.type = type
        self.dataType = dataType
        self.mandatory = False
        self.orConstraint = False
        self.xorConstraint = False
        self.contraints = False

    def __str__(self):
        return 'name={}, type={}, dataType={}, mandatory={}, xorConstraint={}, orConstraint={}, contraints={}'.format(
            self.name,
            self.type,
            self.dataType,
            self.mandatory,
            self.xorConstraint,
            self.orConstraint,
            self.contraints
        )

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
        r'\\DeclareDatamodelFields(\[.*?\]){(.*?)}', re.DOTALL | re.MULTILINE
    )
    _reg_entryFields = re.compile(
        r'\\DeclareDatamodelEntryfields(\[.*?\])?{(.*?)}', re.DOTALL | re.MULTILINE
    )
    _reg_multiscriptEntryFields = re.compile(
        r'\\DeclareDatamodelMultiscriptEntryfields(\[.*?\])?{(.*?)}', re.DOTALL | re.MULTILINE
    )
    # TODO replace the '\n\n' part
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
