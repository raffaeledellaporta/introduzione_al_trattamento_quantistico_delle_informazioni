# Sezione 3 — Istruzioni operative

## Cosa è stato creato

| File | Descrizione |
|---|---|
| `scripts/run_impl.tcl` | Script Tcl Vivado end-to-end: read → synth → opt → place → route → reports → bitstream |
| `build_report_section3.py` | Script Python che legge i `.rpt` di Vivado e popola il PDF Sezione 3 |
| `report/Report_Hadamard_Sezione3.pdf` | PDF Sezione 3 (già pronto in modalità template) |

## Workflow per popolare il PDF con dati REALI di Vivado

### Passo 1 — Lancia Vivado (sul tuo PC dove è installato)

Apri **PowerShell** o **Vivado Tcl Shell**, vai nella cartella del progetto ed esegui:

```powershell
# Da PowerShell, se vivado.bat è nel PATH:
vivado -mode batch -source scripts/run_impl.tcl

# Altrimenti, percorso completo tipico (Vivado 2024.1):
& "C:\Xilinx\Vivado\2024.1\bin\vivado.bat" -mode batch -source scripts/run_impl.tcl
```

Lo script:

1. legge `src/*.vhd` e `constraints/*.xdc`
2. esegue `synth_design` → checkpoint `build/post_synth.dcp`
3. esegue `opt_design`, `place_design`, `phys_opt_design`, `route_design`
4. genera tutti i report in `report/vivado/`:
   - `utilization_synth.rpt`, `utilization_impl.rpt`, `utilization_hier.rpt`
   - `timing_synth.rpt`, `timing_impl.rpt`, `timing_paths.rpt`
   - `power.rpt`
   - `methodology.rpt` (= "Linter" interno di Vivado)
   - `drc.rpt`, `clocks.rpt`
   - `summary.txt` (parser-friendly: PART, T_CLK, WNS, WHS, FMAX)
5. scrive il bitstream in `build/hadamard_gate.bit`

Tempo stimato: **1-3 minuti** sul Spartan-7 (design piccolo).

### Passo 2 — Rigenera il PDF Sezione 3

```powershell
python build_report_section3.py
```

Verrà rigenerato `report/Report_Hadamard_Sezione3.pdf` con **tutti i numeri reali**:

- LUT, FF, DSP, BRAM, IOB, BUFG utilizzati + percentuale di occupazione
- Periodo di clock target, WNS setup, WHS hold, F_max calcolata
- Total / Dynamic / Static Power + Junction Temperature
- Verdetto PASS/FAIL su setup e hold

## In caso di errori

| Sintomo | Causa probabile | Rimedio |
|---|---|---|
| `ERROR: [Common 17-69] vivado not found` | Vivado non nel PATH | Lancia col percorso completo o apri `Vivado Tcl Shell` dal menù Start |
| `read_xdc: PACKAGE_PIN F14 not valid` | Pinout XDC sbagliato per la tua revisione di Boolean Board | Aggiorna i `PACKAGE_PIN` di `constraints/hadamard.xdc` dal *Reference Manual* della board |
| WNS negativo (timing fail) | Path critico troppo lungo | Pipeline-a il DSP: registro fra `sum/diff` e moltiplicazione |
| `INFO: [Synth 8-7080] inferred Multiplier` ma 0 DSP usati | Vivado ha scelto LUT per pochi bit | Forza `(* use_dsp = "yes" *)` davanti a `prod_sum`/`prod_diff` |

## Bonus — Programmare la board

Una volta generato `build/hadamard_gate.bit`:

```tcl
# In una sessione Vivado interattiva
open_hw_manager
connect_hw_server
open_hw_target
set_property PROGRAM.FILE {build/hadamard_gate.bit} [get_hw_devices xc7s50_0]
program_hw_devices [get_hw_devices xc7s50_0]
```

Sulla board vedrai i LED `y0_obs[11:0]` e `y1_obs[11:0]` mostrare il pattern
binario delle ampiezze risultanti dell'applicazione di H allo stato `|0⟩`
(default delle costanti nel top): entrambe le uscite valgono `+0.707` in Q3.8
→ pattern binario `0000 1011 0101` = `0xB5` sui 12 LED di ciascun canale.

