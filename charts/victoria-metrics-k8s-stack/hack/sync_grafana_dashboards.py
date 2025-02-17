#!/usr/bin/env python3
"""Fetch dashboards from provided urls into this chart."""
import json
import textwrap
from os import makedirs, path

import requests
import yaml
from yaml.representer import SafeRepresenter


# https://stackoverflow.com/a/20863889/961092
class LiteralStr(str):
    pass


def change_style(style, representer):
    def new_representer(dumper, data):
        scalar = representer(dumper, data)
        scalar.style = style
        return scalar

    return new_representer


# Source files list
charts = [
    {
        'source': 'https://raw.githubusercontent.com/prometheus-operator/kube-prometheus/master/manifests/grafana-dashboardDefinitions.yaml',
        'destination': '../templates/grafana/dashboards',
        'type': 'yaml'
    },
    {
        'source': 'https://etcd.io/docs/v3.4/op-guide/grafana.json',
        'destination': '../templates/grafana/dashboards',
        'type': 'json'
    },
    {
        'source': 'https://raw.githubusercontent.com/VictoriaMetrics/VictoriaMetrics/master/dashboards/victoriametrics.json',
        'destination': '../templates/grafana/dashboards',
        'type': 'json'
    },
    {
        'source': 'https://raw.githubusercontent.com/VictoriaMetrics/VictoriaMetrics/master/dashboards/vmagent.json',
        'destination': '../templates/grafana/dashboards',
        'type': 'json'
    },
    {
        'source': 'https://raw.githubusercontent.com/VictoriaMetrics/VictoriaMetrics/cluster/dashboards/clusterbytenant.json',
        'destination': '../templates/grafana/dashboards',
        'type': 'json'
    },
]

skip_list = [
    "prometheus.json",
    "prometheus-remote-write.json"
]

# Additional conditions map
condition_map = {
    'grafana-coredns-k8s': ' .Values.coreDns.enabled',
    'etcd': ' .Values.kubeEtcd.enabled',
    'apiserver': ' .Values.kubeApiServer.enabled',
    'controller-manager': ' .Values.kubeControllerManager.enabled',
    'kubelet': ' .Values.kubelet.enabled',
    'proxy': ' .Values.kubeProxy.enabled',
    'scheduler': ' .Values.kubeScheduler.enabled',
    'node-rsrc-use': ' (index .Values "prometheus-node-exporter" "enabled")',
    'node-cluster-rsrc-use': ' (index .Values "prometheus-node-exporter" "enabled")',
    'clusterbytenant': ' .Values.vmcluster.enabled'
}

# standard header
header = '''{{- /*
Generated from '%(name)s' from %(url)s
Do not change in-place! In order to change this file first read following link:
https://github.com/VictoriaMetrics/helm-charts/tree/master/charts/victoria-metrics-k8s-stack/hack
*/ -}}
{{- if and .Values.grafana.enabled .Values.grafana.defaultDashboardsEnabled%(condition)s }}
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: {{ .Release.Namespace }}
  name: {{ printf "%%s-%%s" (include "victoria-metrics-k8s-stack.fullname" $) "%(name)s" | trunc 63 | trimSuffix "-" }}
  labels:
    {{- if $.Values.grafana.sidecar.dashboards.label }}
    {{ $.Values.grafana.sidecar.dashboards.label }}: "1"
    {{- end }}
    app: {{ include "victoria-metrics-k8s-stack.name" $ }}-grafana
{{ include "victoria-metrics-k8s-stack.labels" $ | indent 4 }}
data:
'''


def init_yaml_styles():
    represent_literal_str = change_style('|', SafeRepresenter.represent_str)
    yaml.add_representer(LiteralStr, represent_literal_str)


def escape(s):
    return s.replace("{{", "{{`{{").replace("}}", "}}`}}").replace("{{`{{", "{{`{{`}}").replace("}}`}}", "{{`}}`}}")


def unescape(s):
    return s.replace("\{\{", "{{").replace("\}\}", "}}")


def yaml_str_repr(struct, indent=2):
    """represent yaml as a string"""
    text = yaml.dump(
        struct,
        width=1000,  # to disable line wrapping
        default_flow_style=False  # to disable multiple items on single line
    )
    text = escape(text)  # escape {{ and }} for helm
    text = unescape(text)  # unescape \{\{ and \}\} for templating
    text = textwrap.indent(text, ' ' * indent)
    return text


def patch_json_for_multicluster_configuration(content):
    try:
        content_struct = json.loads(content)
        overwrite_list = []
        for variable in content_struct['templating']['list']:
            if variable['name'] == 'cluster':
                variable['hide'] = ':multicluster:'
            overwrite_list.append(variable)
        content_struct['templating']['list'] = overwrite_list
        content_array = []
        original_content_lines = content.split('\n')
        for i, line in enumerate(json.dumps(content_struct, indent=4).split('\n')):
            if ('[]' not in line and '{}' not in line) or line == original_content_lines[i]:
                content_array.append(line)
                continue

            append = ''
            if line.endswith(','):
                line = line[:-1]
                append = ','

            if line.endswith('{}') or line.endswith('[]'):
                content_array.append(line[:-1])
                content_array.append('')
                content_array.append(' ' * (len(line) - len(line.lstrip())) + line[-1] + append)

        content = '\n'.join(content_array)

        multicluster = content.find(':multicluster:')
        if multicluster != -1:
            content = ''.join((
                content[:multicluster-1],
                '\{\{ if .Values.grafana.sidecar.dashboards.multicluster \}\}0\{\{ else \}\}2\{\{ end \}\}',
                content[multicluster + 15:]
            ))
    except (ValueError, KeyError):
        pass

    return content


def write_group_to_file(resource_name, content, url, destination):
    # initialize header
    lines = header % {
        'name': resource_name,
        'url': url,
        'condition': condition_map.get(resource_name, '')
    }

    content = patch_json_for_multicluster_configuration(content)

    filename_struct = {resource_name + '.json': (LiteralStr(content))}
    # rules themselves
    lines += yaml_str_repr(filename_struct)

    # footer
    lines += '{{- end }}'

    filename = resource_name + '.yaml'
    new_filename = "%s/%s" % (destination, filename)

    # make sure directories to store the file exist
    makedirs(destination, exist_ok=True)

    # recreate the file
    with open(new_filename, 'w') as f:
        f.write(lines)

    print("Generated %s" % new_filename)


def main():
    init_yaml_styles()
    # read the rules, create a new template file per group
    for chart in charts:
        print("Generating dashboards from %s" % chart['source'])
        response = requests.get(chart['source'])
        if response.status_code != 200:
            print('Skipping the file, response code %s not equals 200' % response.status_code)
            continue
        raw_text = response.text

        if chart['type'] == 'yaml':
            yaml_text = yaml.full_load(raw_text)
            groups = yaml_text['items']
            for group in groups:
                for resource, content in group['data'].items():
                    if resource in skip_list:
                        continue
                    write_group_to_file(resource.replace('.json', ''), content, chart['source'], chart['destination'])
        elif chart['type'] == 'json':
            json_text = json.loads(raw_text)
            # is it already a dashboard structure or is it nested (etcd case)?
            flat_structure = bool(json_text.get('annotations'))
            if flat_structure:
                resource = path.basename(chart['source']).replace('.json', '')
                write_group_to_file(resource, json.dumps(json_text, indent=4), chart['source'], chart['destination'])
            else:
                for resource, content in json_text.items():
                    write_group_to_file(resource.replace('.json', ''), json.dumps(content, indent=4), chart['source'], chart['destination'])
    print("Finished")


if __name__ == '__main__':
    main()