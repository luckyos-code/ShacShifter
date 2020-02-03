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
                # print(reg_match.entryTypes)

            if reg_match.fields:
                # print(reg_match.fields)

            if reg_match.entryFields:
                # print(reg_match.entryFields)

            if reg_match.multiscriptEntryFields:
                # print(reg_match.multiscriptEntryFields)

            if reg_match.constraints:
                # print(reg_match.constraints)
                # print(re.findall('(.*?)', reg_match.constraints[0]))

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
        r'\\DeclareDatamodelFields(\[.*?\])?{(.*?)}\n\n', re.DOTALL | re.MULTILINE
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
