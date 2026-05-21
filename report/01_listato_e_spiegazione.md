# Report Progetto — AREA HADAMARD GATE
## Sezione 1 — Listato di codice e spiegazione dettagliata del funzionamento

**Corso:** Introduzione al Trattamento Quantistico delle Informazioni  
**Target hardware:** Boolean Board (Digilent) — FPGA Xilinx Spartan-7 **XC7S50CSGA324-1**  
**Linguaggio:** VHDL (IEEE 1076-2008)  
**Tool di sintesi/implementazione:** AMD/Xilinx Vivado

---

## 1.1  Inquadramento teorico (riassunto)

Il gate di Hadamard è la porta quantistica a 1-qubit più importante nei circuiti
di Deutsch–Jozsa, Grover e Shor: trasforma uno stato di base in una
sovrapposizione bilanciata. La sua matrice è:

$$
H \;=\; \frac{1}{\sqrt{2}}
\begin{bmatrix} 1 & \phantom{-}1 \\ 1 & -1 \end{bmatrix}
$$

Applicata al vettore di stato $|\psi\rangle = [a,\,b]^{T}$ produce:

$$
H\,|\psi\rangle \;=\; \frac{1}{\sqrt{2}}
\begin{bmatrix} a+b \\ a-b \end{bmatrix}
$$

L'obiettivo del progetto è realizzare questa trasformazione **in hardware** su
FPGA, usando **aritmetica a virgola fissa** a 12 bit con segno e 8 bit di parte
frazionaria (formato **Q3.8**: 1 bit di segno, 3 bit interi, 8 bit frazionari),
range $[-8.000\,,\,+7.996]$, risoluzione $1/256 \approx 3.9\cdot10^{-3}$.

La costante $1/\sqrt{2}\approx 0.70710678$ in Q3.8 vale:

$$
\text{round}(0.70710678 \cdot 2^{8}) \;=\; 181
\;=\; \mathtt{0000\_1011\_0101}_2
$$

---

## 1.2  Architettura del progetto

```
                       ┌─────────────────────┐
       A_CONST  ─────► │  REG  a_reg (12b)   │──┐
                       └─────────────────────┘  │
                                                ▼
                       ┌─────────────────────┐  ┌────────────────────────┐
       B_CONST  ─────► │  REG  b_reg (12b)   │─►│   hadamard_core        │
                       └─────────────────────┘  │   (combinatoria)       │
                                                │                        │
                                                │   sum  = a+b           │
                                                │   diff = a-b           │
                                                │   prod_s = sum * 181   │
                                                │   prod_d = diff * 181  │
                                                │   y0 = prod_s >> 8     │
                                                │   y1 = prod_d >> 8     │
                                                └────┬──────────────┬────┘
                                                     ▼              ▼
                                              ┌────────────┐ ┌────────────┐
                                              │ REG y0_reg │ │ REG y1_reg │
                                              └─────┬──────┘ └─────┬──────┘
                                                    ▼              ▼
                                                 y0_obs[11:0]   y1_obs[11:0]
```

La specifica richiede che **tutti gli ingressi e le uscite della top-level
entity siano collegati a registri** (flip-flop). Sono quindi presenti due
banchi di registri: uno in ingresso (`a_reg`, `b_reg`) e uno in uscita
(`y0_reg`, `y1_reg`). Il calcolo combinatorio è incapsulato nel modulo
`hadamard_core`, riusabile e parametrico.

I valori della matrice (1, 1, 1, −1, costante $1/\sqrt{2}$) non sono input ma
**costanti**, come permesso dal SUGGERIMENTO della traccia.

---

## 1.3  Struttura dei file sorgente

| File                                | Ruolo                                                 |
|-------------------------------------|-------------------------------------------------------|
| `src/hadamard_core.vhd`             | Modulo combinatorio: implementa $H\cdot\vec{v}$       |
| `src/hadamard_top.vhd`              | Top-level: registri I/O + costanti A,B + istanza core |
| `sim/tb_hadamard.vhd`               | Testbench behavioral con 4 stimoli                    |
| `constraints/hadamard.xdc`          | Pin assignment per Boolean Board                      |

---

## 1.4  Listato — `hadamard_core.vhd`

```vhdl
--------------------------------------------------------------------------------
-- File         : hadamard_core.vhd
-- Descrizione  : Logica combinatoria del gate di Hadamard 2x2.
--                Calcola H * [a;b] = (1/sqrt(2)) * [a+b ; a-b].
--                Aritmetica a virgola fissa Q3.8 (12 bit signed, 8 frazionari).
-- Target       : Boolean Board (Xilinx Spartan-7 XC7S50)
--------------------------------------------------------------------------------
library IEEE;
    use IEEE.STD_LOGIC_1164.ALL;
    use IEEE.NUMERIC_STD.ALL;

entity hadamard_core is
    generic (
        DATA_WIDTH : integer := 12;   -- larghezza totale del dato
        FRAC_BITS  : integer := 8     -- bit di parte frazionaria
    );
    port (
        a_in   : in  signed(DATA_WIDTH-1 downto 0);  -- ampiezza qubit |0>
        b_in   : in  signed(DATA_WIDTH-1 downto 0);  -- ampiezza qubit |1>
        y0_out : out signed(DATA_WIDTH-1 downto 0);  -- (a+b)/sqrt(2)
        y1_out : out signed(DATA_WIDTH-1 downto 0)   -- (a-b)/sqrt(2)
    );
end entity hadamard_core;

architecture rtl of hadamard_core is

    -- 1/sqrt(2) in Q3.8: round(0.70710678 * 256) = 181 = "00 0010110101"
    constant INV_SQRT2 : signed(DATA_WIDTH-1 downto 0) :=
        to_signed(181, DATA_WIDTH);

    -- Somma e differenza estese di 1 bit per evitare overflow.
    signal sum_ab  : signed(DATA_WIDTH downto 0);
    signal diff_ab : signed(DATA_WIDTH downto 0);

    -- Prodotti completi: (DATA_WIDTH+1) * DATA_WIDTH = 2*DATA_WIDTH+1 bit
    signal prod_sum  : signed(2*DATA_WIDTH downto 0);
    signal prod_diff : signed(2*DATA_WIDTH downto 0);

begin
    sum_ab  <= resize(a_in, DATA_WIDTH+1) + resize(b_in, DATA_WIDTH+1);
    diff_ab <= resize(a_in, DATA_WIDTH+1) - resize(b_in, DATA_WIDTH+1);

    prod_sum  <= sum_ab  * INV_SQRT2;
    prod_diff <= diff_ab * INV_SQRT2;

    y0_out <= resize(shift_right(prod_sum,  FRAC_BITS), DATA_WIDTH);
    y1_out <= resize(shift_right(prod_diff, FRAC_BITS), DATA_WIDTH);
end architecture rtl;
```

### Spiegazione dettagliata

| Riga / Blocco | Cosa fa | Perché è così |
|---|---|---|
| `library IEEE; use NUMERIC_STD.ALL;` | Importa i tipi `signed`/`unsigned` e gli operatori aritmetici **sintetizzabili**. | È lo standard IEEE consigliato: evita l'ambiguità di `std_logic_arith`. |
| `generic DATA_WIDTH, FRAC_BITS` | Parametrizza il modulo. | Permette di riusare lo stesso codice per altri formati Q senza riscriverlo. |
| `a_in, b_in` di tipo `signed` | Ingressi a 12 bit con segno. | I dati sono in Q3.8 → numeri in $[-8, +8)$. |
| `INV_SQRT2 := 181` | Costante a 12 bit signed che codifica $1/\sqrt{2}$. | $\lfloor 0.70710678\cdot 256 \rceil = 181$. Errore di quantizzazione: $|181/256 - 1/\sqrt{2}| \approx 1.3\cdot10^{-4}$. |
| `sum_ab`, `diff_ab` su **13 bit** | Allargano l'operando di 1 bit prima di sommare/sottrarre. | La somma di due numeri a 12 bit può non stare in 12 bit (overflow su $|a|+|b|\ge 8$). Estendendo di 1 bit l'aritmetica è sempre esatta. |
| `resize(x, N)` | Estende il segno mantenendo il valore. | Operatore standard di `NUMERIC_STD`. |
| `prod_sum`, `prod_diff` su **25 bit** | Risultato di `signed(13) * signed(12)` = 25 bit. | Conserva tutta la precisione del prodotto, nessun overflow possibile. |
| `prod_sum <= sum_ab * INV_SQRT2` | Moltiplicazione di un numero Q4.8 (post-estensione) per un Q3.8. | In virgola fissa, $Q_{m_1.f_1}\times Q_{m_2.f_2}$ produce un risultato con $f_1+f_2 = 16$ bit frazionari. Il risultato è in Q?.16. |
| `shift_right(prod, FRAC_BITS)` | Divide per $2^{8}$ → riporta i bit frazionari da 16 a 8. | Riallineamento al formato Q3.8 originale. Lo shift su `signed` è aritmetico (preserva il segno). |
| `resize(..., DATA_WIDTH)` | Tronca/estende a 12 bit. | I bit alti sono replica del segno (dimostrabile dal range degli ingressi), quindi il troncamento non perde informazione utile per i nostri ingressi normalizzati. |

**Aspetto numerico chiave.** Il prodotto `signed(13b) * signed(12b)` produce
25 bit con 16 bit frazionari. Dopo `shift_right(...,8)` restano 17 bit con 8
frazionari; `resize` ne tiene 12. Il sintetizzatore di Vivado, per questa
moltiplicazione, inferisce **un DSP48E1** per ciascun prodotto (2 in totale).

---

## 1.5  Listato — `hadamard_top.vhd`

```vhdl
--------------------------------------------------------------------------------
-- File         : hadamard_top.vhd
-- Descrizione  : Top-level entity del gate di Hadamard 2x2 con registri di
--                ingresso e di uscita (richiesto dalla specifica).
--                Ingressi 'a_in' e 'b_in' costanti come da SUGGERIMENTO della
--                traccia.
-- Target       : Boolean Board (Xilinx Spartan-7 XC7S50CSGA324-1)
--------------------------------------------------------------------------------
library IEEE;
    use IEEE.STD_LOGIC_1164.ALL;
    use IEEE.NUMERIC_STD.ALL;

entity hadamard_top is
    generic (
        DATA_WIDTH : integer := 12;
        FRAC_BITS  : integer := 8
    );
    port (
        clk    : in  std_logic;                              -- 100 MHz Boolean Board
        rst    : in  std_logic;                              -- reset sincrono attivo alto
        y0_obs : out std_logic_vector(DATA_WIDTH-1 downto 0);
        y1_obs : out std_logic_vector(DATA_WIDTH-1 downto 0)
    );
end entity hadamard_top;

architecture rtl of hadamard_top is

    -- COSTANTI DELLO STATO DI INGRESSO (SUGGERIMENTO)
    -- Stato |0> = [1.0 ; 0.0]  ->  in Q3.8:  1.0 = 256, 0.0 = 0
    constant A_CONST : signed(DATA_WIDTH-1 downto 0) := to_signed(256, DATA_WIDTH);
    constant B_CONST : signed(DATA_WIDTH-1 downto 0) := to_signed(  0, DATA_WIDTH);

    signal a_reg, b_reg     : signed(DATA_WIDTH-1 downto 0);
    signal y0_c, y1_c       : signed(DATA_WIDTH-1 downto 0);
    signal y0_reg, y1_reg   : signed(DATA_WIDTH-1 downto 0);

    component hadamard_core is
        generic (DATA_WIDTH : integer := 12;
                 FRAC_BITS  : integer := 8);
        port (a_in   : in  signed(DATA_WIDTH-1 downto 0);
              b_in   : in  signed(DATA_WIDTH-1 downto 0);
              y0_out : out signed(DATA_WIDTH-1 downto 0);
              y1_out : out signed(DATA_WIDTH-1 downto 0));
    end component;
begin
    -- Registri di ingresso
    p_in_reg : process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                a_reg <= (others => '0');
                b_reg <= (others => '0');
            else
                a_reg <= A_CONST;
                b_reg <= B_CONST;
            end if;
        end if;
    end process p_in_reg;

    -- Core combinatorio
    u_core : hadamard_core
        generic map (DATA_WIDTH => DATA_WIDTH, FRAC_BITS  => FRAC_BITS)
        port map    (a_in => a_reg, b_in => b_reg,
                     y0_out => y0_c, y1_out => y1_c);

    -- Registri di uscita
    p_out_reg : process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                y0_reg <= (others => '0');
                y1_reg <= (others => '0');
            else
                y0_reg <= y0_c;
                y1_reg <= y1_c;
            end if;
        end if;
    end process p_out_reg;

    y0_obs <= std_logic_vector(y0_reg);
    y1_obs <= std_logic_vector(y1_reg);
end architecture rtl;
```

### Spiegazione dettagliata

1. **Porte fisiche** (`clk`, `rst`, `y0_obs`, `y1_obs`)
   - `clk` e `rst` sono gli unici input osservabili sulla board; il vettore di
     stato è interno (costante), come consentito dalla traccia.
   - Le uscite sono `std_logic_vector` per poterle pinnare direttamente ai LED
     della Boolean Board nel file `.xdc`.

2. **Costanti del vettore stato**
   - `A_CONST = 256`, `B_CONST = 0` → in Q3.8 valgono **+1.0** e **0.0**, cioè
     lo stato $|0\rangle$.
   - Cambiando solo queste due righe si testano in hardware tutti gli stati
     ($|1\rangle$, $|+\rangle$, $|-\rangle$, ecc.).

3. **Registri di ingresso `p_in_reg`**
   - Processo sensibile al solo `clk` → inferisce flip-flop sincroni con
     **reset sincrono** attivo alto.
   - Forzando i registri all'inizio del clock domain, blindiamo il timing del
     core: il sintetizzatore vede ingressi *clean* (no skew di routing).

4. **Istanza `u_core`**
   - Mappatura diretta dei registri sui port del core.
   - I generic vengono propagati, così il top resta scalabile.

5. **Registri di uscita `p_out_reg`**
   - Stesso schema: catturano `y0_c`/`y1_c` al fronte di salita.
   - Garantiscono che il *path* combinatorio del core sia un unico stage tra
     due flip-flop → consente di calcolare $F_\text{max}$ in modo pulito sul
     report di timing.

6. **Driver delle uscite**
   - `y0_obs <= std_logic_vector(y0_reg)` è puramente *concorrente*: il
     cast `signed → std_logic_vector` ha **costo zero** (stesso pattern di
     bit), serve solo a soddisfare la dichiarazione di porta.

---

## 1.6  Listato — `tb_hadamard.vhd` (testbench behavioral)

```vhdl
library IEEE;
    use IEEE.STD_LOGIC_1164.ALL;
    use IEEE.NUMERIC_STD.ALL;

entity tb_hadamard is
end entity tb_hadamard;

architecture sim of tb_hadamard is
    constant DATA_WIDTH : integer := 12;
    constant FRAC_BITS  : integer := 8;
    constant CLK_PERIOD : time    := 10 ns;

    component hadamard_core is
        generic (DATA_WIDTH : integer := 12;
                 FRAC_BITS  : integer := 8);
        port (a_in   : in  signed(DATA_WIDTH-1 downto 0);
              b_in   : in  signed(DATA_WIDTH-1 downto 0);
              y0_out : out signed(DATA_WIDTH-1 downto 0);
              y1_out : out signed(DATA_WIDTH-1 downto 0));
    end component;

    signal a_in, b_in : signed(DATA_WIDTH-1 downto 0) := (others => '0');
    signal y0,   y1   : signed(DATA_WIDTH-1 downto 0);

    function to_q (val : real) return signed is
    begin
        return to_signed(integer(val * real(2**FRAC_BITS)), DATA_WIDTH);
    end function;

    procedure check (constant name : string;
                     signal   got  : signed;
                     constant exp  : real) is
        variable exp_q : signed(DATA_WIDTH-1 downto 0);
        variable diff  : integer;
    begin
        exp_q := to_q(exp);
        diff  := to_integer(got) - to_integer(exp_q);
        if diff < 0 then diff := -diff; end if;
        if diff <= 2 then
            report name & " OK (got=" & integer'image(to_integer(got)) &
                   "  exp=" & integer'image(to_integer(exp_q)) & ")"
                severity note;
        else
            report name & " FAIL (got=" & integer'image(to_integer(got)) &
                   "  exp=" & integer'image(to_integer(exp_q)) & ")"
                severity error;
        end if;
    end procedure;
begin
    dut : hadamard_core
        generic map (DATA_WIDTH => DATA_WIDTH, FRAC_BITS => FRAC_BITS)
        port map    (a_in => a_in, b_in => b_in, y0_out => y0, y1_out => y1);

    stim_proc : process
    begin
        -- TEST 1: |0> = [1 ; 0] -> [+0.707 ; +0.707]
        a_in <= to_q(1.0); b_in <= to_q(0.0);
        wait for CLK_PERIOD;
        check("TEST1 |0> y0", y0,  0.70710678);
        check("TEST1 |0> y1", y1,  0.70710678);

        -- TEST 2: |1> = [0 ; 1] -> [+0.707 ; -0.707]
        a_in <= to_q(0.0); b_in <= to_q(1.0);
        wait for CLK_PERIOD;
        check("TEST2 |1> y0", y0,  0.70710678);
        check("TEST2 |1> y1", y1, -0.70710678);

        -- TEST 3: |+> = [0.707 ; 0.707] -> [1.0 ; 0.0]
        a_in <= to_q( 0.70710678); b_in <= to_q( 0.70710678);
        wait for CLK_PERIOD;
        check("TEST3 |+> y0", y0,  1.0);
        check("TEST3 |+> y1", y1,  0.0);

        -- TEST 4: |-> = [0.707 ; -0.707] -> [0.0 ; 1.0]
        a_in <= to_q( 0.70710678); b_in <= to_q(-0.70710678);
        wait for CLK_PERIOD;
        check("TEST4 |-> y0", y0,  0.0);
        check("TEST4 |-> y1", y1,  1.0);

        report "Simulazione completata." severity note;
        wait;
    end process;
end architecture sim;
```

### Spiegazione dettagliata

- **Entità senza port** (`entity tb_hadamard is end;`) — è la convenzione
  standard per un testbench: il *test bench* non si interfaccia col mondo
  esterno, contiene solo stimoli e DUT.
- **Funzione `to_q(real)`** — converte un numero in virgola mobile nel suo
  equivalente Q3.8. È usata **solo in simulazione** (non sintetizzabile) per
  rendere la lettura dei test molto più leggibile (es. `to_q(0.707)` invece di
  `to_signed(181,12)`).
- **Procedura `check`** — confronta il valore osservato con quello atteso
  ammettendo un errore massimo di **2 LSB** ($\approx 0.0078$). La tolleranza
  serve perché:
  1. La costante `INV_SQRT2 = 181/256` è essa stessa quantizzata.
  2. Il prodotto seguito da `shift_right` introduce un troncamento.
- **4 stimoli** — sono i 4 stati di base più rappresentativi per validare
  l'**involutività** di H ($H^2 = I$):
  - Test 1 / 2 verificano la trasformazione di $|0\rangle$ e $|1\rangle$ nelle
    sovrapposizioni $|+\rangle$ e $|-\rangle$.
  - Test 3 / 4 verificano il caso inverso: applicando $H$ a $|+\rangle$ /
    $|-\rangle$ si torna esattamente a $|0\rangle$ / $|1\rangle$.

Tabella di sintesi dei test:

| #  | Ingresso `[a;b]`        | Stato in   | Uscita attesa `[y0;y1]` | Stato out  |
|----|-------------------------|------------|--------------------------|------------|
| 1  | `[+1.000 ;  0.000]`     | $|0\rangle$| `[+0.707 ; +0.707]`      | $|+\rangle$|
| 2  | `[ 0.000 ; +1.000]`     | $|1\rangle$| `[+0.707 ; -0.707]`      | $|-\rangle$|
| 3  | `[+0.707 ; +0.707]`     | $|+\rangle$| `[+1.000 ;  0.000]`      | $|0\rangle$|
| 4  | `[+0.707 ; -0.707]`     | $|-\rangle$| `[ 0.000 ; +1.000]`      | $|1\rangle$|

---

## 1.7  Listato — `constraints/hadamard.xdc`

```tcl
## Clock 100 MHz
set_property -dict { PACKAGE_PIN F14 IOSTANDARD LVCMOS33 } [get_ports clk]
create_clock -name sys_clk -period 10.000 [get_ports clk]

## Reset sincrono attivo alto: BTN0
set_property -dict { PACKAGE_PIN J2  IOSTANDARD LVCMOS33 } [get_ports rst]

## y0_obs[0..11] -> LED0..LED11 ... (mapping completo nel file)
## y1_obs[0..11] -> LED12..LED15 + 8 PMOD
```

### Spiegazione dettagliata

- **`create_clock -period 10.000`**: dichiara il clock di sistema a **100 MHz**
  (Boolean Board), indispensabile perché il *timing engine* di Vivado calcoli
  lo slack e quindi $F_\text{max}$.
- **`IOSTANDARD LVCMOS33`**: standard elettrico di default dei banchi I/O
  della Spartan-7 sulla Boolean Board (3.3 V).
- I pin LED riportano in tempo reale lo stato dei registri di uscita
  `y0_reg`/`y1_reg`; per gli ingressi (costanti) non serve allocare pin.

---

## 1.8  Cosa è stato dimostrato in questa sezione

- Il design rispetta integralmente la specifica:
  - top entity con I/O **registrati**;
  - tutti i segnali di dato a **12 bit signed Q3.8**;
  - matrice / stato in **costanti** della top entity (SUGGERIMENTO);
  - target Boolean Board, sintesi Vivado.
- Il modulo è **parametrico** (`DATA_WIDTH`, `FRAC_BITS`) e quindi facilmente
  estendibile.
- Il calcolo è numericamente corretto (errore massimo $\le 2$ LSB) ed è
  inferenza automatica di DSP48 in fase di sintesi.

> Nelle prossime sezioni (2 — Linter, 3 — Implementazione, 4 — Testbench) si
> riporteranno gli output di Vivado e gli screenshot della simulazione.

