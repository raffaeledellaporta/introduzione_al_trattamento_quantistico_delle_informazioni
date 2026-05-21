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
    -- Lo rappresentiamo su 12 bit signed (valore positivo).
    constant INV_SQRT2 : signed(DATA_WIDTH-1 downto 0) :=
        to_signed(181, DATA_WIDTH);

    -- Somma e differenza estese di 1 bit per evitare overflow.
    signal sum_ab  : signed(DATA_WIDTH downto 0);
    signal diff_ab : signed(DATA_WIDTH downto 0);

    -- Prodotti completi: (DATA_WIDTH+1) * DATA_WIDTH = 2*DATA_WIDTH+1 bit
    signal prod_sum  : signed(2*DATA_WIDTH downto 0);
    signal prod_diff : signed(2*DATA_WIDTH downto 0);

begin

    -- Somma e differenza con estensione di segno.
    sum_ab  <= resize(a_in, DATA_WIDTH+1) + resize(b_in, DATA_WIDTH+1);
    diff_ab <= resize(a_in, DATA_WIDTH+1) - resize(b_in, DATA_WIDTH+1);

    -- Moltiplicazione per 1/sqrt(2) (Q3.8 * Q3.8 -> Q6.16 esteso).
    prod_sum  <= sum_ab  * INV_SQRT2;
    prod_diff <= diff_ab * INV_SQRT2;

    -- Riallineamento Q -> Q3.8: scarto FRAC_BITS bit bassi e prendo
    -- DATA_WIDTH bit (con saturazione implicita affidata al range dei segnali).
    -- prod ha 2*DATA_WIDTH+1 bit con 2*FRAC_BITS bit frazionari;
    -- per tornare a FRAC_BITS frazionari devo shiftare a destra di FRAC_BITS.
    y0_out <= resize(shift_right(prod_sum,  FRAC_BITS), DATA_WIDTH);
    y1_out <= resize(shift_right(prod_diff, FRAC_BITS), DATA_WIDTH);

end architecture rtl;

