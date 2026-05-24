--------------------------------------------------------------------------------
-- File : hadamard_top.vhd
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity hadamard_top is
generic(
    data_width : integer := 12;
    frac_bits  : integer := 8
);
port(
    clk : in std_logic;
    rst : in std_logic;

    -- solo pin realmente disponibili
    y0_obs : out std_logic_vector(5 downto 0);
    y1_obs : out std_logic_vector(5 downto 0)
);
end entity;

architecture rtl of hadamard_top is

constant a_const : signed(data_width-1 downto 0)
    := to_signed(256,data_width);

constant b_const : signed(data_width-1 downto 0)
    := to_signed(0,data_width);

signal a_reg,b_reg : signed(data_width-1 downto 0);

signal y0_c,y1_c : signed(data_width-1 downto 0);

signal y0_reg,y1_reg : signed(data_width-1 downto 0);

component hadamard_core
generic(
    data_width : integer := 12;
    frac_bits  : integer := 8
);
port(
    a_in   : in signed(data_width-1 downto 0);
    b_in   : in signed(data_width-1 downto 0);

    y0_out : out signed(data_width-1 downto 0);
    y1_out : out signed(data_width-1 downto 0)
);
end component;

begin

------------------------------------------------------------------
-- input registers
------------------------------------------------------------------

p_in_reg : process(clk)
begin

    if rising_edge(clk) then

        if rst='1' then
            a_reg<=(others=>'0');
            b_reg<=(others=>'0');
        else
            a_reg<=a_const;
            b_reg<=b_const;
        end if;

    end if;

end process;

------------------------------------------------------------------
-- core
------------------------------------------------------------------

u_core : hadamard_core
generic map(
    data_width => data_width,
    frac_bits  => frac_bits
)
port map(
    a_in   => a_reg,
    b_in   => b_reg,
    y0_out => y0_c,
    y1_out => y1_c
);

------------------------------------------------------------------
-- output registers
------------------------------------------------------------------

p_out_reg : process(clk)
begin

    if rising_edge(clk) then

        if rst='1' then
            y0_reg<=(others=>'0');
            y1_reg<=(others=>'0');
        else
            y0_reg<=y0_c;
            y1_reg<=y1_c;
        end if;

    end if;

end process;

------------------------------------------------------------------
-- esporta solo bit realmente collegati
------------------------------------------------------------------

y0_obs(0) <= y0_reg(0);
y0_obs(1) <= y0_reg(1);
y0_obs(2) <= y0_reg(4);
y0_obs(3) <= y0_reg(6);
y0_obs(4) <= y0_reg(7);
y0_obs(5) <= y0_reg(11);

y1_obs(0) <= y1_reg(1);
y1_obs(1) <= y1_reg(2);
y1_obs(2) <= y1_reg(3);
y1_obs(3) <= y1_reg(4);
y1_obs(4) <= y1_reg(6);
y1_obs(5) <= y1_reg(7);

end architecture;