# Cambios aplicados para diversificar los pares del top (correlación)

Cada cambio modifica solo parámetros que ya se extraen como features en `run_analysis.py`.

**Objetivo cumplido:** max |r| **< 0,95** (actualmente **0,9475**). cos_dist mín **> 0,05** (0,0534). Pares con cos_dist < 0,05: **0**.

| Par (r alto) | Escenario A | Cambios en A | Escenario B | Cambios en B |
|--------------|-------------|---------------|-------------|---------------|
| **U11–V7** (0.99) | U11 | workDayLength 25200, nrOfMeetingSpots 8, transmitRange 8 | V7 | workDayLength 32400, transmitRange 14, nrOfMeetingSpots 12 |
| **T10–T15** (0.99) | T10 | world 6500×4500, nrofHosts 50, buffer 25M, transmitRange 8 | T15 | world 5000×3800, nrofHosts 38, event interval 100–280, size 15k–60k, transmitRange 13 |
| **T11–T4** (0.99) | T4 | msgTtl 5, world 6500×4800, speed 0.4–1.0 | T11 | world 5000×4000, speed 0.7–1.5, wait 50–250, Events 30–90, 5k–60k |
| **U4–U8** (0.99) | U4 | workDayLength 25200, nrOfOffices 8, transmitRange 12 | U8 | nrOfOffices 14 (Group+Group2) |
| **T1–T9** (0.99) | T1 | world 5500×4200, nrofHosts 40 | T9 | world 6500×5000, nrofHosts 50, transmitRange 8 |
| **V1–V2** (0.98) | V1 | bufferSize 30M (Group+Group1) | V2 | (sin cambio; ya transmitRange 14) |
| **T13–T9/T1** | T13 | world 7000×5500, nrofHosts 32, speed 0.4–1.0, wait 80–320, transmitRange 6 | — | — |
| **S3–T5** (0.96) | S3 | world 4500×3600, buffer 40M, Events 70–180, 20k–100k | — | — |
| **R5–D6** (0.96) | R5 | transmitRange 12, buffer 40M | D6 | world 7000×5000, transmitRange 8 |
| **U3–C5** (0.95) | U3 | transmitRange 9, workDayLength 25200 | C5 | (ya transmitRange 15, nrOfMeetingSpots 20) |

Tras aplicar: ejecutar `run_analysis.py --corpus corpus_v1 --phase all` y revisar `reports/correlation_report.txt`.
