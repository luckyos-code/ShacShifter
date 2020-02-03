import logging
import re

class _RegExLib:
    """Set up regular expressions"""
    # use https://regexper.com to visualise these if required
    _reg_entryTypes = re.compile(r'\\DeclareDatamodelEntrytypes(\[.*?])?{(.*?)}', re.DOTALL)
    _reg_grade = re.compile(r'Grade = (.*)\n')
    _reg_name_score = re.compile(r'(Name|Score)')

    __slots__ = ['entryTypes', 'grade', 'name_score']

    def __init__(self, line):
        # check whether line has a positive match with all of the regular expressions
        self.entryTypes = self._reg_entryTypes.match(line)
        self.grade = self._reg_grade.match(line)
        self.name_score = self._reg_name_score.search(line)

class BibLaTeXDefParser:
    """A parser for the BibLaTeX DEF specification."""

    logger = logging.getLogger('ShacShifter.BibLaTeXDefParser')

    def __init__(self):
        # Future node shapes
        self.entryTypes = {}
        # Future property shapes
        self.entryFields = {}

    def parseDef(self, inputFilePath):
        """Parse the BibLaTeX Specification.

        args: string inputFilePath
        returns: list of dictionaries for entryTypes and entryFields
        """
        reg_match = _RegExLib("""\\DeclareDatamodelEntrytypes{
            article,
            artwork,
            audio,
            bibnote,
            book,
            bookinbook,
            booklet,
            collection,
            commentary,
            customa,
            customb,
            customc,
            customd,
            custome,
            customf,
            dataset,
            inbook,
            incollection,
            inproceedings,
            inreference,
            image,
            jurisdiction,
            legal,
            legislation,
            letter,
            manual,
            misc,
            movie,
            music,
            mvcollection,
            mvreference,
            mvproceedings,
            mvbook,
            online,
            patent,
            performance,
            periodical,
            proceedings,
            reference,
            report,
            review,
            set,
            software,
            standard,
            suppbook,
            suppcollection,
            suppperiodical,
            thesis,
            unpublished,
            video}""")

        if reg_match.entryTypes:
            entryTypes = reg_match.entryTypes.group(2)
            print(entryTypes)

        with open(inputFilePath, 'r') as file:
            line = next(file)
            while line:
                reg_match = _RegExLib(line)

                if reg_match.entryTypes:
                    entryTypes = reg_match.entryTypes.group(1)
                    print(entryTypes)

                if reg_match.grade:
                    grade = reg_match.grade.group(1)
                    grade = int(grade)

                if reg_match.name_score:
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

                line = next(file, None)

        return 
