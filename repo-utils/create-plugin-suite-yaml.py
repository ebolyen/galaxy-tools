#!/usr/bin/env python

import os
import sys
import json
from xml.sax.saxutils import quoteattr

import yaml
import qiime2.sdk


# SO: https://stackoverflow.com/a/39681672
class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


def main(plugin_id, categories, destination):
    pm = qiime2.sdk.PluginManager()
    plugin = pm.get_plugin(id=plugin_id)
    suite_name = os.path.basename(destination.rstrip("/"))

    shed = {
        'owner': 'q2d2',
        'homepage_url': plugin.website,
        'remote_repository_url': (f'https://github.com/qiime2/galaxy-tools'
                                  f'/tree/main/tools/{suite_name}'),
        'categories': categories,
        'auto_tool_repositories': {
            'name_template': '{{ tool_id }}',
            'description_template': 'Galaxy tool for QIIME 2 action:'
                                    ' \'{{tool_name}}\'.'
        },
        'suite': {
            'name': suite_name,
            'description': f'Galaxy suite for QIIME 2 plugin: '
                           f'\'{plugin.name}\'.'
                           f' {plugin.short_description}',
            'long_description': plugin.description
        }
    }
    # Fix quoting for XML as these are converted blindly on the toolshed
    # causing inconsistent states:
    shed['suite']['description'] = quoteattr(shed['suite']['description'])
    # long_description doesn't appear to be written into the
    # tool_dependencies.xml, so it is probably fine.

    with open(os.path.join(destination, '.shed.yml'), 'w') as fh:
        fh.write(yaml.dump(shed, default_flow_style=False, sort_keys=False,
                 Dumper=Dumper))

    print(json.dumps(shed), flush=True)

    # HACK: not all tools have example data, and while q2galaxy will create the
    # empty directory, git won't keep it.
    test_dir = os.path.join(destination, 'test-data/')
    if not os.listdir(test_dir):
        with open(os.path.join(test_dir, '.gitkeep'), 'w') as fh:
            pass


if __name__ == '__main__':
    _, plugin_id, categories, destination = sys.argv
    main(plugin_id, categories.split(','), destination)
