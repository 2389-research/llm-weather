# LLM Weather Report — {{ .Title }}

{{ with .Params.headline }}{{ . }}{{ end }}

{{ with .Params.drift -}}
## Drift Alerts
{{ range . -}}
- {{ .type }}: {{ .model }} on {{ .prompt }}
{{ end }}
{{ end -}}

## Scorecard

{{ $promptIDs := slice -}}
{{ range $model, $prompts := .Params.scorecard -}}
  {{ range $pid, $_ := $prompts -}}
    {{ if not (in $promptIDs $pid) -}}
      {{ $promptIDs = $promptIDs | append $pid -}}
    {{ end -}}
  {{ end -}}
{{ end -}}

| Model | {{ range $promptIDs }}{{ . }} | {{ end }}
|-------|{{ range $promptIDs }}------|{{ end }}
{{ range $model, $prompts := .Params.scorecard -}}
| {{ $model }} | {{ range $pid := $promptIDs }}{{ $entry := index $prompts $pid }}{{ if $entry }}{{ if eq $entry.correct true }}✓ ({{ $entry.score }}){{ else if eq $entry.correct false }}✗ ({{ $entry.score }}){{ else }}—{{ end }}{{ else }}—{{ end }} | {{ end }}
{{ end }}

{{ with .Params.status -}}
## Model Status
{{ range $model, $state := . -}}
- {{ if eq $state "up" }}↑{{ else if eq $state "down" }}↓{{ else }}→{{ end }} **{{ $model }}**: {{ $state }}
{{ end }}
{{ end -}}
