{{/*
Expand the name of the chart.
*/}}
{{- define "auth-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "auth-service.fullname" -}}
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
{{- define "auth-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "auth-service.labels" -}}
helm.sh/chart: {{ include "auth-service.chart" . }}
{{ include "auth-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "auth-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "auth-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "auth-service.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "auth-service.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "auth-service.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "postgresql://%s:%s@%s-postgresql:5432/%s" .Values.postgresql.auth.username .Values.postgresql.auth.password (include "auth-service.fullname" .) .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.secrets.databaseUrl }}
{{- end }}
{{- end }}

{{/*
OAuth2 Issuer URL
*/}}
{{- define "auth-service.oauth2IssuerUrl" -}}
{{- if .Values.ingress.enabled }}
{{- $host := index .Values.ingress.hosts 0 }}
{{- if .Values.ingress.tls }}
{{- printf "https://%s" $host.host }}
{{- else }}
{{- printf "http://%s" $host.host }}
{{- end }}
{{- else }}
{{- .Values.config.oauth2IssuerUrl }}
{{- end }}
{{- end }}

{{/*
OAuth2 JWKS URI
*/}}
{{- define "auth-service.oauth2JwksUri" -}}
{{- printf "%s/.well-known/jwks.json" (include "auth-service.oauth2IssuerUrl" .) }}
{{- end }}

