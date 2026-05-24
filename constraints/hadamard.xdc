## ============================================================================
## hadamard.xdc
## Spartan-7 Boolean Board
## Device: xc7s50csga324-1
## ============================================================================

## ----------------------------------------------------------------------------
## CLOCK 100 MHz
## ----------------------------------------------------------------------------
set_property PACKAGE_PIN F14 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]

create_clock -name sys_clk -period 10.000 [get_ports clk]

## ----------------------------------------------------------------------------
## RESET
## ----------------------------------------------------------------------------
set_property PACKAGE_PIN J2 [get_ports rst]
set_property IOSTANDARD LVCMOS33 [get_ports rst]

## ----------------------------------------------------------------------------
## y0_obs[0..5]
## ----------------------------------------------------------------------------
set_property PACKAGE_PIN A8  [get_ports {y0_obs[0]}]
set_property PACKAGE_PIN A9  [get_ports {y0_obs[1]}]
set_property PACKAGE_PIN R7  [get_ports {y0_obs[2]}]
set_property PACKAGE_PIN T5  [get_ports {y0_obs[3]}]
set_property PACKAGE_PIN R6  [get_ports {y0_obs[4]}]
set_property PACKAGE_PIN T11 [get_ports {y0_obs[5]}]

## ----------------------------------------------------------------------------
## y1_obs[0..5]
## ----------------------------------------------------------------------------
set_property PACKAGE_PIN U12 [get_ports {y1_obs[0]}]
set_property PACKAGE_PIN V12 [get_ports {y1_obs[1]}]
set_property PACKAGE_PIN V13 [get_ports {y1_obs[2]}]
set_property PACKAGE_PIN V14 [get_ports {y1_obs[3]}]
set_property PACKAGE_PIN U15 [get_ports {y1_obs[4]}]
set_property PACKAGE_PIN V15 [get_ports {y1_obs[5]}]

## ----------------------------------------------------------------------------
## IOSTANDARD
## ----------------------------------------------------------------------------

set_property IOSTANDARD LVCMOS33 [get_ports y0_obs[*]]
set_property IOSTANDARD LVCMOS33 [get_ports y1_obs[*]]