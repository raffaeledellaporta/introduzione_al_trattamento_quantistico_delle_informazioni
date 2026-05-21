# Progetto: AREA HADAMARD GATE
**Corso:** Introduzione al Trattamento Quantistico delle Informazioni  
**Target:** Boolean Board (Digilent) – FPGA Xilinx Spartan-7 XC7S50CSGA324-1  
**Linguaggio:** VHDL-93 / VHDL-2008  
**Tool:** AMD/Xilinx **Vivado** (consigliato 2023.x o successivo)

---

## 1. Cos'è e come funziona

Il gate di Hadamard 2x2 è:

```
        1   | 1   1 |
 H  = ----- |       |
       √2   | 1  -1 |
```

Dato un vettore di stato `[a ; b]`, il blocco calcola:

```
 y0 = (a + b) / √2
 y1 = (a − b) / √2
```

### Formato dei dati
- **12 bit signed**, **8 bit frazionari** → formato a virgola fissa **Q3.8**  
  (1 bit segno + 3 bit interi + 8 bit frazionari).  
- Range rappresentabile: **[−8.0 ; +7.996]**, risoluzione **1/256 ≈ 0.0039**.
- Costante `1/√2 ≈ 0.70710678` in Q3.8: `round(0.70710678 · 256) = 181` → binario `0000_1011_0101`.

### Architettura
```
              ┌──────────────┐
   A_CONST →─►│ in-reg (FF)  │──┐
              └──────────────┘  │   ┌───────────────────┐
                                ├──►│  hadamard_core    │
              ┌──────────────┐  │   │  (combinatoria:   │   ┌──────────────┐
   B_CONST →─►│ in-reg (FF)  │──┘   │   sum, diff,      │──►│ out-reg (FF) │──► y0_obs
              └──────────────┘      │   *INV_SQRT2,     │   └──────────────┘
                                    │   >> 8)           │   ┌──────────────┐
                                    │                   │──►│ out-reg (FF) │──► y1_obs
                                    └───────────────────┘   └──────────────┘
```
- Tutti i `port` della top-level passano per **registri** (richiesta del progetto).
- Gli ingressi `a` e `b` sono presi come `constant` dentro la top entity (come suggerito nella traccia).

---

## 2. Struttura del progetto

```
introduzione_al_trattamento_quantistico_delle_informazioni/
├─ src/
│  ├─ hadamard_core.vhd      ← core combinatorio (matrice)
│  └─ hadamard_top.vhd       ← top-level con registri + costanti A,B
├─ sim/
│  └─ tb_hadamard.vhd        ← testbench behavioral (4 test)
├─ constraints/
│  └─ hadamard.xdc           ← pin assignment Boolean Board
└─ README.md                 ← (questo file)
```

---

## 3. Come creare il progetto in Vivado

1. **Apri Vivado** → `Create Project` → nome `hadamard_gate` → tipo **RTL Project**.
2. **Add Sources** → aggiungi i due file in `src/` (top = `hadamard_top`).
3. **Add Simulation Sources** → aggiungi `sim/tb_hadamard.vhd`.
4. **Add Constraints** → aggiungi `constraints/hadamard.xdc`.
5. **Parts** → seleziona **xc7s50csga324-1** (Boolean Board).
6. Imposta in `Settings → General → Target language` = **VHDL**,  
   e in `Simulation → xsim.simulate.runtime` = `200 ns`.

---

## 4. Cosa mettere nel report PDF (passo-passo)

### 4.1 Listato di codice + spiegazione
Copia integralmente i 3 file `.vhd`. Per ciascuno descrivi:
- **`hadamard_core.vhd`**  
  - costante `INV_SQRT2 = 181` (cioè `1/√2` in Q3.8);
  - `sum_ab`, `diff_ab` su `DATA_WIDTH+1` bit per evitare overflow di a±b;
  - moltiplicazione `signed * signed` (Q3.8 × Q3.8 = Q6.16);
  - `shift_right(prod, FRAC_BITS)` per riallineare a Q3.8;
  - `resize(..., DATA_WIDTH)` per tornare a 12 bit.
- **`hadamard_top.vhd`**  
  - costanti `A_CONST`, `B_CONST` (default: stato |0⟩);
  - processi `p_in_reg`, `p_out_reg` → registri sincroni con reset;
  - istanza del core `u_core`;
  - conversione `signed → std_logic_vector` per i pin.
- **`tb_hadamard.vhd`**  
  - funzione `to_q(real)` per convertire numeri reali in Q3.8;
  - procedura `check` con tolleranza di 2 LSB (errore di quantizzazione);
  - 4 stimoli che corrispondono agli stati `|0⟩, |1⟩, |+⟩, |−⟩`.

### 4.2 Risultato del Linter
In Vivado: `Reports → Report Methodology` **e** `Tools → Report → Report Code Analysis` (oppure
`Reports → Lint Run` se usi Vitis HLS / un linter esterno).  
Per il VHDL puro, in Vivado:
- `Flow Navigator → Synthesis → Run Synthesis` → quando termina,  
  `Reports → Report Methodology` → salva come PDF/TXT e includilo nel report.
- Atteso: **0 errori, 0 warning critici**. Eventuali "INFO" su DSP inferenza vanno bene.

### 4.3 Risultati di implementazione
Esegui `Run Implementation`, poi:
- **Utilizzo risorse FPGA**:  
  `Reports → Report Utilization` → screenshot/tabella con LUT, FF, DSP, BRAM, IO.  
  *Atteso (ordine di grandezza):* < 50 LUT, ~ 48 FF (2×12 in + 2×12 out), 2 DSP48.
- **Frequenza massima di clock**:  
  `Reports → Report Timing Summary` → leggi **WNS** (Worst Negative Slack) del clock `sys_clk`.  
  Calcolo: `Fmax = 1 / (T_clk − WNS)`. Es. con `T_clk = 10 ns` e `WNS = +2.5 ns` →  
  `Fmax = 1 / 7.5 ns ≈ 133 MHz`.
- **Dissipazione di potenza**:  
  Dopo l'implementation: `Reports → Report Power` → screenshot della tabella  
  *Total On-Chip Power* (Dynamic + Static). Tipico: 70–150 mW per un design così piccolo.

### 4.4 Risultati Testbench (Behavioral)
- `Flow Navigator → Simulation → Run Simulation → Run Behavioral Simulation`.
- Apri il **waveform**: aggiungi i segnali `a_in`, `b_in`, `y0`, `y1` (formato **Signed Decimal** o **Fixed Point Q3.8**).
- Lancia `run 200 ns`.
- Nella console TCL vedrai i `report` con `TEST1..TEST4 OK`.  
- **Esporta lo screenshot** del waveform e i log della console; includili nel PDF.

I 4 test sono già scritti e coprono:
| Test | Ingresso `[a;b]`        | Stato logico | Uscita attesa `[y0;y1]`     |
|------|-------------------------|--------------|-----------------------------|
| 1    | `[1.0 ; 0.0]`           | `|0⟩`        | `[+0.707 ; +0.707]`         |
| 2    | `[0.0 ; 1.0]`           | `|1⟩`        | `[+0.707 ; −0.707]`         |
| 3    | `[+0.707 ; +0.707]`     | `|+⟩`        | `[+1.000 ;  0.000]`         |
| 4    | `[+0.707 ; −0.707]`     | `|−⟩`        | `[ 0.000 ; +1.000]`         |

Il test 3 e 4 dimostrano l'**involutività** di H (HH = I).

---

## 5. Struttura suggerita del report PDF

1. **Frontespizio** (titolo, nome, matricola, corso).
2. **Introduzione teorica** (½ pagina): cos'è il gate di Hadamard, ruolo nei circuiti quantistici (Deutsch, Grover…).
3. **Specifica del progetto**: 12 bit signed Q3.8, target Boolean Board, registri I/O.
4. **Architettura**: schema a blocchi (puoi rifare in Draw.io quello del README).
5. **Listato VHDL** con commenti (3 sezioni: core, top, tb).
6. **Linter / Methodology report** (screenshot).
7. **Sintesi & Implementation**:
   - utilizzo risorse (tabella),
   - timing report (WNS + Fmax calcolato),
   - power report (screenshot).
8. **Simulazione**: waveform + tabella test + log console.
9. **Conclusioni**: discussione errore di quantizzazione (≤ 2 LSB = ≤ 0.008).

---

## 6. Note e possibili estensioni

- Se vuoi un blocco *riusabile* per gate Hadamard a 2 qubit (H⊗H), basta istanziare 4 volte questo core e sommare opportunamente (matrice 4×4).
- Per evitare l'inferenza di DSP e usare solo LUT, aggiungi `(* use_dsp = "no" *)` davanti ai segnali `prod_sum`/`prod_diff`.
- Per migliorare il timing puoi *pipeline-are* il core inserendo un registro tra `sum/diff` e la moltiplicazione (3 stadi totali).

---

## 7. Comandi rapidi (TCL)

Dalla console Tcl di Vivado puoi automatizzare:

```tcl
# Da lanciare nella cartella del progetto
read_vhdl  -vhdl2008 [glob src/*.vhd]
read_xdc   constraints/hadamard.xdc
synth_design -top hadamard_top -part xc7s50csga324-1
report_utilization -file reports/utilization.rpt
report_timing_summary -file reports/timing.rpt
opt_design
place_design
route_design
report_power -file reports/power.rpt
write_bitstream -force hadamard_top.bit
```

