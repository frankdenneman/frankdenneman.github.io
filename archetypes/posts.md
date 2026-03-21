---
title: "{{ humanize (replaceRE "^\\d{4}-\\d{2}-\\d{2}-" "" .Name) }}"
date: {{ .Date }}
url: "/{{ .Name }}/"
aliases:
  - "/posts/{{ .Name }}/"
categories: ["ai"]
track: "AI Infrastructure"
draft: true
---
