from pyapollo.constant import properties_config_file_format, yaml_config_file_format, default_config_file_format
from pyapollo.format_parser import PropertiesContentParser, DefaultContentParser, YAMLContentParser

__format_parser_map = {
    default_config_file_format: DefaultContentParser,
    properties_config_file_format: PropertiesContentParser,
    yaml_config_file_format: YAMLContentParser,
}


def add_format_parser(config_file_format_key, format_parser):
    __format_parser_map[config_file_format_key] = format_parser


def get_format_parser(config_file_format_key):
    return __format_parser_map.get(config_file_format_key, DefaultContentParser)
