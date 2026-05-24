# Traffic profiles (TP01–TP12)

**Status:** stable | **Updated:** 2026-05-20 11:41 UTC

## Purpose

Document traffic overlays.

## Content

Traffic is **synthetic**, applied via `Events.nrof` / `MessageEventGenerator` on top of each base `.settings`.

| TP | Name | Intent |
|----|------|--------|
| TP01 | Baseline | Reference load |
| TP02 | LowLoad | Sparse messages |
| TP03 | ManySmall | High rate, small size |
| TP04 | FewLarge | Large messages (stress) |
| TP05 | CriticalTTL | Short TTL |
| TP06 | OneToMany | Fan-out |
| TP07 | BurstWindow | Mid-sim burst |
| TP08 | HubTarget | Hub traffic |
| TP09 | Bimodal | Two generators |
| TP10 | Storm | Congestion |
| TP11 | ManyToOne | Many-to-one |
| TP12 | GroupToGroup | Cross-group (partition control) |

Validation: [tp_validation_report.md](../analysis/reports/tp_validation_report.md)


## Internal links

[08-Message-Generation-and-Analysis-Window](08-Message-Generation-and-Analysis-Window)

## Open questions

TP04 size 500k–2M sufficient after revision?

## Paper usage

Methods — traffic workload.
