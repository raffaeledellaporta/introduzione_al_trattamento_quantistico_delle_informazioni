--------------------------------------------------------------------------------
-- File         : tb_hadamard.vhd
-- Descrizione  : Testbench BEHAVIORAL del gate di Hadamard 2x2.
--                Verifica 4 tipologie di input:
--                  1) Stato |0>  = [1.0 ; 0.0]     -> attesa [+0.707 ; +0.707]
--                  2) Stato |1>  = [0.0 ; 1.0]     -> attesa [+0.707 ; -0.707]
--                  3) Stato |+>  = [0.707 ; 0.707] -> attesa [+1.0   ;  0.0  ]
--                  4) Stato |->  = [0.707 ;-0.707] -> attesa [ 0.0   ; +1.0  ]
--------------------------------------------------------------------------------

library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

entity tb_hadamard is
end entity tb_hadamard;

architecture sim of tb_hadamard is

  constant data_width : integer := 12;
  constant frac_bits  : integer := 8;
  constant clk_period : time    := 10 ns;   -- 100 MHz

  -- DUT: istanzio direttamente il core per poter cambiare gli ingressi.
  component hadamard_core is
    generic (
      data_width : integer := 12;
      frac_bits  : integer := 8
    );
    port (
      a_in   : in    signed(DATA_WIDTH - 1 downto 0);
      b_in   : in    signed(DATA_WIDTH - 1 downto 0);
      y0_out : out   signed(DATA_WIDTH - 1 downto 0);
      y1_out : out   signed(DATA_WIDTH - 1 downto 0)
    );
  end component hadamard_core;

  signal a_in, b_in : signed(data_width - 1 downto 0) := (others => '0');
  signal y0,   y1   : signed(data_width - 1 downto 0);

  -- Funzione di utilita': converte un real (numero in virgola mobile)
  -- nella sua rappresentazione Q3.8 a 12 bit signed.

  function to_q (
    val : real
  ) return signed is
  begin

    return to_signed(integer(val * real(2 ** FRAC_BITS)), DATA_WIDTH);

  end function to_q;

  -- Procedura di check con tolleranza (LSB).

  procedure check (
    constant name : string;
    signal   got  : signed;
    constant exp  : real
  ) is

    variable exp_q : signed(DATA_WIDTH - 1 downto 0);
    variable diff  : integer;

  begin

    exp_q := to_q(exp);
    diff  := to_integer(got) - to_integer(exp_q);

    if (diff < 0) then
      diff := -diff;
    end if;

    if (diff <= 2) then
      report name & " OK (got=" & integer'image(to_integer(got)) &
             "  exp=" & integer'image(to_integer(exp_q)) & ")"
        severity note;
    else
      report name & " FAIL (got=" & integer'image(to_integer(got)) &
             "  exp=" & integer'image(to_integer(exp_q)) & ")"
        severity error;
    end if;

  end procedure check;

begin

  ----------------------------------------------------------------------------
  -- Istanza DUT
  ----------------------------------------------------------------------------
  dut : component hadamard_core
    generic map (
      data_width => DATA_WIDTH, frac_bits => FRAC_BITS
    )
    port map (
      a_in   => a_in,
      b_in   => b_in,
      y0_out => y0,
      y1_out => y1
    );

  ----------------------------------------------------------------------------
  -- Stimoli
  ----------------------------------------------------------------------------
  stim_proc : process is
  begin

    ------------------------------------------------------------------
    -- Test 1: |0> = [1 ; 0] -> [+1/sqrt2 ; +1/sqrt2] ~ [+0.707 ; +0.707]
    ------------------------------------------------------------------
    a_in <= to_q(1.0);
    b_in <= to_q(0.0);
    wait for clk_period;
    check("TEST1 |0> y0", y0,  0.70710678);
    check("TEST1 |0> y1", y1,  0.70710678);

    ------------------------------------------------------------------
    -- Test 2: |1> = [0 ; 1] -> [+1/sqrt2 ; -1/sqrt2]
    ------------------------------------------------------------------
    a_in <= to_q(0.0);
    b_in <= to_q(1.0);
    wait for clk_period;
    check("TEST2 |1> y0", y0,  0.70710678);
    check("TEST2 |1> y1", y1, -0.70710678);

    ------------------------------------------------------------------
    -- Test 3: |+> = [0.707 ; 0.707] -> [1.0 ; 0.0]
    ------------------------------------------------------------------
    a_in <= to_q(0.70710678);
    b_in <= to_q(0.70710678);
    wait for clk_period;
    check("TEST3 |+> y0", y0,  1.0);
    check("TEST3 |+> y1", y1,  0.0);

    ------------------------------------------------------------------
    -- Test 4: |-> = [0.707 ; -0.707] -> [0.0 ; 1.0]
    ------------------------------------------------------------------
    a_in <= to_q(0.70710678);
    b_in <= to_q(-0.70710678);
    wait for clk_period;
    check("TEST4 |-> y0", y0,  0.0);
    check("TEST4 |-> y1", y1,  1.0);

    report "Simulazione completata."
      severity note;
    wait;

  end process stim_proc;

end architecture sim;

