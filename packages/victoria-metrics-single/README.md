# victoria-metrics-single

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![AppVersion: 1.31.2](https://img.shields.io/badge/AppVersion-1.31.2-informational?style=flat-square)

Victoria Metrics Single version - high-performance, cost-effective and scalable TSDB, long-term remote storage for Prometheus

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rbac.create | bool | `true` |  |
| rbac.extraLabels | object | `{}` |  |
| rbac.namespaced | bool | `false` |  |
| rbac.pspEnabled | bool | `true` |  |
| server.affinity | object | `{}` |  |
| server.enabled | bool | `true` |  |
| server.extraArgs | object | `{}` |  |
| server.fullnameOverride | string | `nil` |  |
| server.image.pullPolicy | string | `"IfNotPresent"` |  |
| server.image.repository | string | `"victoriametrics/victoria-metrics"` |  |
| server.image.tag | string | `"v1.31.2"` |  |
| server.ingress.annotations | object | `{}` |  |
| server.ingress.enabled | bool | `false` |  |
| server.ingress.extraLabels | object | `{}` |  |
| server.ingress.hosts | list | `[]` |  |
| server.ingress.tls | list | `[]` |  |
| server.name | string | `"server"` |  |
| server.nodeSelector | object | `{}` |  |
| server.persistentVolume.accessModes[0] | string | `"ReadWriteOnce"` |  |
| server.persistentVolume.annotations | object | `{}` |  |
| server.persistentVolume.enabled | bool | `true` |  |
| server.persistentVolume.existingClaim | string | `""` |  |
| server.persistentVolume.mountPath | string | `"/storage"` |  |
| server.persistentVolume.size | string | `"16Gi"` |  |
| server.persistentVolume.subPath | string | `""` |  |
| server.podAnnotations | object | `{}` |  |
| server.podManagementPolicy | string | `"OrderedReady"` |  |
| server.priorityClassName | string | `""` |  |
| server.resources | object | `{}` |  |
| server.retentionPeriod | int | `1` |  |
| server.securityContext | object | `{}` |  |
| server.service.annotations | object | `{}` |  |
| server.service.clusterIP | string | `""` |  |
| server.service.externalIPs | list | `[]` |  |
| server.service.labels | object | `{}` |  |
| server.service.loadBalancerIP | string | `""` |  |
| server.service.loadBalancerSourceRanges | list | `[]` |  |
| server.service.servicePort | int | `8428` |  |
| server.service.type | string | `"ClusterIP"` |  |
| server.serviceMonitor.annotations | object | `{}` |  |
| server.serviceMonitor.enabled | bool | `false` |  |
| server.serviceMonitor.extraLabels | object | `{}` |  |
| server.statefulSet.enabled | bool | `true` |  |
| server.statefulSet.podManagementPolicy | string | `"OrderedReady"` |  |
| server.statefulSet.service.annotations | object | `{}` |  |
| server.statefulSet.service.labels | object | `{}` |  |
| server.statefulSet.service.servicePort | int | `8428` |  |
| server.terminationGracePeriodSeconds | int | `60` |  |
| server.tolerations | list | `[]` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.extraLabels | object | `{}` |  |

