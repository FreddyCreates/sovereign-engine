# Julia Terminal THESIS

Release state: `prototype_scaffold`

## Purpose

Julia Terminal THESIS is the local serious-research version of THESIS.

It lets researchers audit local folders and repositories without relying on repository-host AI summaries.

## Intended Commands

```bash
thesis scan .
thesis audit repo ./my-repo
thesis claims paper.md
thesis packet build ./source
thesis print paper.md --pdf
thesis hash ./packet
thesis verify ./claim_matrix.json
```

## Why Julia

Julia signals scientific computing, reproducibility, mathematical seriousness, and terminal-native research practice. It is a strong fit for researchers who already work with simulation, numerical methods, data, notebooks, and local compute.

## Prototype Scope

The initial Julia scaffold should:

- walk a repo or folder
- classify files
- detect evidence-bearing files
- create a claim/evidence checklist
- emit markdown and JSON packet files
- compute SHA-256 hashes
- prepare a print/export handoff

## Install Draft

```bash
git clone https://github.com/FreddyCreates/JOURNAL.git
cd JOURNAL/thesis/julia-terminal
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. bin/thesis.jl scan ../..
```
