{{/*
Expand the name of the chart.
*/}}
{{- define "config-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "config-service.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "config-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "config-service.labels" -}}
helm.sh/chart: {{ include "config-service.chart" . }}
{{ include "config-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "config-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "config-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "config-service.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "config-service.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret
*/}}
{{- define "config-service.secretName" -}}
{{- printf "%s-secrets" (include "config-service.fullname" .) }}
{{- end }}

{{/*
Create the name of the configmap
*/}}
{{- define "config-service.configMapName" -}}
{{- printf "%s-config" (include "config-service.fullname" .) }}
{{- end }}

{{/*
Create the image name
*/}}
{{- define "config-service.image" -}}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- end }}

{{/*
Create the name of the persistent volume claim
*/}}
{{- define "config-service.pvcName" -}}
{{- printf "%s-storage" (include "config-service.fullname" .) }}
{{- end }}

