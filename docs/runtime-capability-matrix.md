# Runtime Capability Matrix

- Python: 3.10.4
- Workspace: `/Users/reidar/Documents/Agent System`

| Capability | Status | Evidence | Disposition |
| --- | --- | --- | --- |
| repo read access | yes | workspace root is /Users/reidar/Documents/Agent System | use directly |
| repo write access | yes | patch-based file edits are available | use directly |
| shell access | yes | commands can be run through the local shell | use directly |
| filesystem search | yes | `rg` and Python filesystem APIs are available | use directly |
| file editing | yes | repository files can be created and patched | use directly |
| git access | yes | git repository detected or git executable available | use directly |
| network access | yes | runtime reports network access enabled | defer for v1 |
| package install ability | partial | shell is available, but v1 avoids dependencies | defer safely |
| local database availability | yes | sqlite 3.37.2 | use directly |
| browser control | partial | runtime exposes browser-capable tools, not needed for v1 | defer safely |
| screenshot or vision support | partial | runtime can inspect local images/screenshots | defer safely |
| desktop input control | partial | runtime exposes computer-use tools | defer safely |
| tool-calling support | yes | Codex tools are available in this session | use directly |
| sub-agent support | partial | available through deferred tools/skills when needed | defer safely |
| long-running background execution | partial | terminal sessions can run, durable scheduler absent | emulate later |
| cron or scheduled execution | no | no repository scheduler implemented yet | defer safely |
| webhook or event trigger support | no | no external listener implemented yet | defer safely |
| persistent storage | yes | repo files and SQLite are available | use directly |
| UI or dashboard rendering | partial | CLI/markdown available; hosted dashboard absent | emulate in files |
| secret management | partial | no harness-level secret vault yet | defer safely |
| approval and interruption controls | partial | human chat approval exists; policy engine absent | defer safely |
| multi-machine support | no | no hub/worker network protocol yet | defer safely |
