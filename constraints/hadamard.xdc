## ----------------------------------------------------------------------------
## File         : hadamard.xdc
## Descrizione  : Constraints per Boolean Board (Digilent, Spartan-7 XC7S50)
## Note         : Modifica i pin in base alla tua versione del manuale della
##                Boolean Board. Qui usiamo i nomi di rete del reference manual
##                Digilent (clock 100 MHz su pin F14, BTN0 = J2, LED0..15).
## ----------------------------------------------------------------------------

## Clock 100 MHz
set_property -dict { PACKAGE_PIN F14  IOSTANDARD LVCMOS33 } [get_ports clk]
create_clock -name sys_clk -period 10.000 [get_ports clk]

## Reset sincrono attivo alto: BTN0
set_property -dict { PACKAGE_PIN J2   IOSTANDARD LVCMOS33 } [get_ports rst]

## ----------------------------------------------------------------------------
## y0_obs[11..0] -> LED0..LED11
## ----------------------------------------------------------------------------
set_property -dict { PACKAGE_PIN A8   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[0]}]
set_property -dict { PACKAGE_PIN A9   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[1]}]
set_property -dict { PACKAGE_PIN R8   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[2]}]
set_property -dict { PACKAGE_PIN T8   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[3]}]
set_property -dict { PACKAGE_PIN R7   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[4]}]
set_property -dict { PACKAGE_PIN T7   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[5]}]
set_property -dict { PACKAGE_PIN T5   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[6]}]
set_property -dict { PACKAGE_PIN R6   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[7]}]
set_property -dict { PACKAGE_PIN T9   IOSTANDARD LVCMOS33 } [get_ports {y0_obs[8]}]
set_property -dict { PACKAGE_PIN R10  IOSTANDARD LVCMOS33 } [get_ports {y0_obs[9]}]
set_property -dict { PACKAGE_PIN T10  IOSTANDARD LVCMOS33 } [get_ports {y0_obs[10]}]
set_property -dict { PACKAGE_PIN T11  IOSTANDARD LVCMOS33 } [get_ports {y0_obs[11]}]

## ----------------------------------------------------------------------------
## y1_obs[11..0] -> LED12..LED15 + 8 PMOD (es. JA)
## NB: la Boolean Board ha 16 LED; rimappa secondo necessita'.
## ----------------------------------------------------------------------------
set_property -dict { PACKAGE_PIN U13  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[0]}]
set_property -dict { PACKAGE_PIN U12  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[1]}]
set_property -dict { PACKAGE_PIN V12  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[2]}]
set_property -dict { PACKAGE_PIN V13  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[3]}]
set_property -dict { PACKAGE_PIN V14  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[4]}]
set_property -dict { PACKAGE_PIN U14  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[5]}]
set_property -dict { PACKAGE_PIN U15  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[6]}]
set_property -dict { PACKAGE_PIN V15  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[7]}]
set_property -dict { PACKAGE_PIN W15  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[8]}]
set_property -dict { PACKAGE_PIN W16  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[9]}]
set_property -dict { PACKAGE_PIN W17  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[10]}]
set_property -dict { PACKAGE_PIN W18  IOSTANDARD LVCMOS33 } [get_ports {y1_obs[11]}]

