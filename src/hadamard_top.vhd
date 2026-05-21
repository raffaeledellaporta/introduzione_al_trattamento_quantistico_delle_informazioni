--------------------------------------------------------------------------------
-- File         : hadamard_top.vhd
-- Descrizione  : Top-level entity del gate di Hadamard 2x2 con registri di
--                ingresso e di uscita (richiesto dalla specifica).
--                Ingressi 'a_in' e 'b_in' costanti come da SUGGERIMENTO della
--                traccia (matrice / vettore stato fissi nella top entity).
-- Target       : Boolean Board (Xilinx Spartan-7 XC7S50CSGA324-1)
--------------------------------------------------------------------------------

library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

entity hadamard_top is
  generic (
    data_width : integer := 12;
    frac_bits  : integer := 8
  );
  port (
    clk : in    std_logic; -- 100 MHz Boolean Board
    rst : in    std_logic; -- reset sincrono attivo alto
    -- Uscite osservabili su LED / pin: parte intera (4 bit MSB) di ciascuna uscita
    y0_obs : out   std_logic_vector(data_width - 1 downto 0);
    y1_obs : out   std_logic_vector(data_width - 1 downto 0)
  );
end entity hadamard_top;

architecture rtl of hadamard_top is

  ----------------------------------------------------------------------------
  -- COSTANTI DELLO STATO DI INGRESSO (come da SUGGERIMENTO)
  -- Stato |0> = [1.0 ; 0.0]  ->  in Q3.8:  1.0 = 256, 0.0 = 0
  ----------------------------------------------------------------------------
  constant a_const : signed(data_width - 1 downto 0) := to_signed(256, data_width); -- 1.0
  constant b_const : signed(data_width - 1 downto 0) := to_signed(  0, data_width); -- 0.0

  -- Registri di ingresso
  signal a_reg,  b_reg : signed(data_width - 1 downto 0);

  -- Segnali combinatori dal core
  signal y0_c,   y1_c : signed(data_width - 1 downto 0);

  -- Registri di uscita
  signal y0_reg, y1_reg : signed(data_width - 1 downto 0);

  ----------------------------------------------------------------------------
  -- Istanza del core combinatorio
  ----------------------------------------------------------------------------
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

begin

  ----------------------------------------------------------------------------
  -- Registri di ingresso: campionano le costanti (struttura richiesta
  -- dalla specifica). Il sintetizzatore manterrà comunque i flip-flop
  -- perche' collegati al pin di clock e reset.
  ----------------------------------------------------------------------------
  p_in_reg : process (clk) is
  begin

    if rising_edge(clk) then
      if (rst = '1') then
        a_reg <= (others => '0');
        b_reg <= (others => '0');
      else
        a_reg <= a_const;
        b_reg <= b_const;
      end if;
    end if;

  end process p_in_reg;

  ----------------------------------------------------------------------------
  -- Core combinatorio
  ----------------------------------------------------------------------------
  u_core : component hadamard_core
    generic map (
      data_width => data_width,
      frac_bits  => frac_bits
    )
    port map (
      a_in   => a_reg,
      b_in   => b_reg,
      y0_out => y0_c,
      y1_out => y1_c
    );

  ----------------------------------------------------------------------------
  -- Registri di uscita
  ----------------------------------------------------------------------------
  p_out_reg : process (clk) is
  begin

    if rising_edge(clk) then
      if (rst = '1') then
        y0_reg <= (others => '0');
        y1_reg <= (others => '0');
      else
        y0_reg <= y0_c;
        y1_reg <= y1_c;
      end if;
    end if;

  end process p_out_reg;

  -- Driver dei pin (conversione signed -> std_logic_vector)
  y0_obs <= std_logic_vector(y0_reg);
  y1_obs <= std_logic_vector(y1_reg);

end architecture rtl;

