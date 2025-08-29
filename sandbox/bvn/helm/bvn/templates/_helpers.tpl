{{- define "bvn.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "bvn.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "bvn.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "bvn.labels" -}}
app.kubernetes.io/name: {{ include "bvn.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "bvn.selectorLabels" -}}
app.kubernetes.io/name: {{ include "bvn.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "bvn.secretName" -}}
{{ include "bvn.fullname" . }}-secrets
{{- end -}}



{{- define "bvn.image" -}}
{{- if .Values.global.imageRegistry -}}
{{- printf "%s/%s" .Values.global.imageRegistry .Values.image.repository -}}
{{- else -}}
{{- .Values.image.repository -}}
{{- end -}}
{{- end -}}
