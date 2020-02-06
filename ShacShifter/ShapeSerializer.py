from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .ShapeParser import ShapeParser
import logging
import rdflib


class Mapping:
    """The Mapping class."""
    def __init__(self, schemaPath):
        self.schemaPath = schemaPath
        self.namespaces = []
        self.nodes = {}
        self.properties = {}
        self.parseMapping()

    def parseMapping(self):
        with open(self.schemaPath, 'r') as schema:
            line = schema.readline()
            while line:
                if '# Namespaces' in line:
                    schema.readline()
                    line = schema.readline()
                    while not line[:2] == '##':
                        if line[:3] == 'ns_':
                            namespace = '@prefix ' + line[3:].replace('\n','').replace('=', ': <', 1) + '> .'
                            self.namespaces.append(namespace)
                        line = schema.readline()
                if '# Type mappings' in line:
                    schema.readline()
                    line = schema.readline()
                    while not line[:2] == '##':
                        if line.strip() and line[:1] != '#':
                            nodeMapping = line.split('=', 1)
                            self.nodes[nodeMapping[0]] = nodeMapping[1].strip('\n')
                        line = schema.readline()
                if '# Field mappings' in line:
                    schema.readline()
                    line = schema.readline()
                    while line and not line[:2] == '##':
                        if line.strip() and line[:1] != '#':
                            propertyMapping = line.split('=', 1)
                            self.properties[propertyMapping[0]] = propertyMapping[1].strip('\n')
                        line = schema.readline()
                line = schema.readline()


class ShapeSerializer:
    """A serializer for SHACL shapes."""

    logger = logging.getLogger('ShacShifter.ShapeSerializer')
    shapes = []
    mapping = None
    outputfile = None

    def __init__(self, entryTypes, outputfile=None, mappingSchema='', baseUri=None):
        """Initialize the Serializer and parse des BibLaTeXDefParser results.

        args: entry fields
              string outputfile
        """
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close()
        except Exception:
            self.logger.error('Can\'t write to file {}'.format(outputfile))
            self.logger.error('Content will be printed to sys.')

        self.commonNS = [
            '@prefix sh: <http://www.w3.org/ns/shacl#> .',
            '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .',
            '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .',
            '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .'
        ]
        self.mapping = Mapping(mappingSchema)
        self.baseUri = 'http://example.org/bib/' if (baseUri is None) else baseUri

        for node in self.mapping.nodes:
            if node.lower() in entryTypes:
                shape = self.stringShape(node, entryTypes[node.lower()])
                self.shapes.append(shape)

    def write(self):
        """Write RDForms to file or sysout."""
        if self.outputfile:
            fp = open(self.outputfile, 'w')
            nsString = '\n'.join(set(self.commonNS + self.mapping.namespaces))
            #print(nsString + '\n')
            fp.write(nsString + '\n\n')
            shapesString = '\n\n'.join(self.shapes)
            #print(shapesString + '\n\n')
            fp.write(shapesString + '\n')
            fp.close()
        else:
            nsString = '\n'.join(self.commonNS + self.mapping.namespaces)
            print(nsString + '\n\n')
            shapesString = '\n'.join(self.shapes)
            print(shapesString + '\n')

    def stringShape(self, node, entryType):
        """Converts entryType to shape string."""
        shapeString = ''
        shapeString += (
            '<{}{}Shape>\n'.format(self.baseUri, node) +
            '\ta sh:NodeShape ;\n' +
            '\tsh:targetClass {} ;\n'.format(self.mapping.nodes[node]) +
            '\tsh:name "{}" ;\n'.format(node)
        )
        for prop in self.mapping.properties:
            for field in entryType.fields:
                if prop.lower() == field.name:
                    shapeString += (
                        '\tsh:property [\n' +
                        '\t\tsh:path {} ;\n'.format(self.mapping.properties[prop]) +
                        '\t\tsh:name "{}" ;\n'.format(prop)
                    )
                    #if prop.title() in self.mapping.nodes:
                    #    shapeString += '\t\tsh:class {} ;\n'.format(self.mapping.nodes[prop.title()])
                    if field.mandatory:
                        shapeString += '\t\tsh:minCount 1 ;\n'
                    shapeString += '\t] ;\n'
        shapeString = shapeString[:-3]  + '.'
        return shapeString

    def createShape(self, entryType):
        """Evaluate an entryType.

        args:   EntryType entryType
        """
        # TODO
        def addNodeLabel():
            label = {'en': 'Template: ' + nodeShape.uri}
            if nodeShape.isSet['targetClass']:
                label = {'en': 'Create new Instance of: ' + ', '.join(nodeShape.targetClass)}
            if nodeShape.isSet['targetNode']:
                label = {'en': 'Edit Instance of: ' + ', '.join(nodeShape.targetNode)}
            if nodeShape.isSet['targetObjectsOf']:
                label = {'en': ', '.join(nodeShape.targetObjectsOf)}
            if nodeShape.isSet['targetSubjectsOf']:
                label = {'en': 'Edit: '', '.join(nodeShape.targetSubjectsOf)}
            return label

        def addTemplates():
            """Check Propertey Shapes to fill the templates."""
            templates = []
            for propertyShape in nodeShape.properties:
                template = self.getTemplate(propertyShape)
                if template is not None:
                    templates.append(template)
            return templates

        bundle = RDFormsTemplateBundle()
        bundle.label = addNodeLabel()
        if nodeShape.isSet['message']:
            bundle.description = nodeShape.message
        bundle.root = nodeShape.uri
        if len(nodeShape.properties) > 0:
            bundle.templates = addTemplates()

        return bundle

    def getShape(self, field):
        """Evaluate a Field to serialize a property shape section.

        args:   Field field
        return: PropertyShape
        """
        # TODO
        def initTemplateItem():
            if propertyShape.isSet['shIn']:
                item = fillChoiceItem(RDFormsChoiceItem())
            else:
                item = fillTextItem(RDFormsTextItem())

            return fillBasicItemValues(item)

        def fillChoiceItem(item):
            item = fillBasicItemValues(item)
            item.cardinality = getCardinality()
            item.choices = self.getChoices(propertyShape)
            return item

        def fillTextItem(item):
            item.cardinality = getCardinality()
            return item

        def fillBasicItemValues(item):
            item.id = propertyShape.path
            item.label = propertyShape.name if propertyShape.isSet['name'] else (
                                    propertyShape.path.rsplit('/', 1)[-1])
            item.description = getDescription()
            return item

        def getDescription():
            if propertyShape.isSet['message']:
                return propertyShape.message
            elif propertyShape.isSet['description']:
                return {'en': propertyShape.description}
            else:
                return {'en': 'This is about ' + propertyShape.path}

        def getCardinality():
            cardinality = {'min': 0, 'pref': 1}

            if propertyShape.isSet['minCount']:
                cardinality['min'] = propertyShape.minCount

            if propertyShape.isSet['maxCount']:
                cardinality['max'] = propertyShape.maxCount

            return cardinality

        if isinstance(propertyShape.path, dict):
            # TODO handle complex paths (inverse, oneOrMorePath ...)
            self.logger.info('Complex path not supported, yet')
        elif isinstance(propertyShape.path, list):
            # TODO handle sequence paths
            self.logger.info('Sequence path not supported, yet')
        else:
            item = initTemplateItem()
            return item

    def getChoices(self, propertyShape):
        """Search for choice candidates in propertyShape and return a choice list.

        args: PropertyShape propertyShape
        returns: list
        """
        # TODO
        choices = []
        for choice in propertyShape.shIn:
            choiceItem = RDFormsChoiceExpression()
            choiceItem.label = choice
            choiceItem.value = choice
            choiceItem.children = set(propertyShape.shIn) - set([choice])
            choices.append(choiceItem)

        return choices
