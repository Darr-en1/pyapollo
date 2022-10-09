import yaml


class DefaultContentParser:
    @staticmethod
    def parse(configContent):
        return configContent


class PropertiesContentParser(DefaultContentParser):
    pass


class YAMLContentParser:
    @staticmethod
    def parse(configContent):
        content = configContent["content"]
        return yaml.safe_load(content)
