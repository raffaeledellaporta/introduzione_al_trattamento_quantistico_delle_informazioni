################################################################################
# File         : run_impl.tcl
# Descrizione  : Flusso end-to-end Vivado per il progetto AREA HADAMARD GATE.
#                Esegue: read sources, synthesis, opt/place/route, report di
#                utilization / timing / power, e scrittura del bitstream.
# Target       : Boolean Board (Xilinx Spartan-7 XC7S50CSGA324-1)
# Uso          : Da terminale (NON dalla GUI Vivado!)
#                   vivado -mode batch -source scripts/run_impl.tcl
#                Oppure dalla console Tcl di Vivado:
#                   source scripts/run_impl.tcl
################################################################################

# ----------------------------------------------------------------------------
# Parametri di progetto
# ----------------------------------------------------------------------------
set PROJ_NAME   "hadamard_gate"
set PART        "xc7s50csga324-1"
set TOP_MODULE  "hadamard_top"

# Percorsi (relativi alla cartella del progetto = cwd)
set SRC_DIR     "src"
set SIM_DIR     "sim"
set XDC_DIR     "constraints"
set RPT_DIR     "report/vivado"
set OUT_DIR     "build"

file mkdir $RPT_DIR
file mkdir $OUT_DIR

puts "================================================================================"
puts "  AREA HADAMARD GATE - Vivado end-to-end flow"
puts "  Part : $PART"
puts "  Top  : $TOP_MODULE"
puts "================================================================================"

# ----------------------------------------------------------------------------
# 1. Lettura sorgenti
# ----------------------------------------------------------------------------
puts "\n--- 1/6  Reading sources ---"
read_vhdl -vhdl2008 [glob $SRC_DIR/*.vhd]
read_xdc  [glob $XDC_DIR/*.xdc]

# (i file di simulazione NON vanno passati alla sintesi)
set_property top $TOP_MODULE [current_fileset]

# ----------------------------------------------------------------------------
# 2. Sintesi
# ----------------------------------------------------------------------------
puts "\n--- 2/6  Synthesis ---"
synth_design -top $TOP_MODULE -part $PART -flatten_hierarchy rebuilt

write_checkpoint -force $OUT_DIR/post_synth.dcp
report_utilization        -file $RPT_DIR/utilization_synth.rpt
report_timing_summary     -file $RPT_DIR/timing_synth.rpt
report_methodology        -file $RPT_DIR/methodology.rpt

# ----------------------------------------------------------------------------
# 3. Optimization
# ----------------------------------------------------------------------------
puts "\n--- 3/6  Optimization ---"
opt_design

# ----------------------------------------------------------------------------
# 4. Place
# ----------------------------------------------------------------------------
puts "\n--- 4/6  Placement ---"
place_design
phys_opt_design

# ----------------------------------------------------------------------------
# 5. Route
# ----------------------------------------------------------------------------
puts "\n--- 5/6  Routing ---"
route_design

write_checkpoint -force $OUT_DIR/post_route.dcp

# ----------------------------------------------------------------------------
# 6. Report finali (post-implementation)
# ----------------------------------------------------------------------------
puts "\n--- 6/6  Reports & bitstream ---"
report_utilization        -file $RPT_DIR/utilization_impl.rpt
report_utilization -hierarchical -file $RPT_DIR/utilization_hier.rpt
report_timing_summary     -file $RPT_DIR/timing_impl.rpt
report_timing -sort_by group -max_paths 5 -path_type summary \
                          -file $RPT_DIR/timing_paths.rpt
report_clocks             -file $RPT_DIR/clocks.rpt
report_power              -file $RPT_DIR/power.rpt
report_drc                -file $RPT_DIR/drc.rpt

# Bitstream (utile per programmare effettivamente la board)
write_bitstream -force $OUT_DIR/${PROJ_NAME}.bit

# ----------------------------------------------------------------------------
# Stampa a video di un riepilogo "essenziale"
# ----------------------------------------------------------------------------
puts "\n================================================================================"
puts "  RIEPILOGO POST-IMPLEMENTATION"
puts "================================================================================"

set wns_setup [get_property SLACK [get_timing_paths -setup -max_paths 1]]
set whs_hold  [get_property SLACK [get_timing_paths -hold  -max_paths 1]]
set clk_obj   [lindex [get_clocks] 0]
set clk_per   [get_property PERIOD $clk_obj]
set fmax_mhz  [expr {1000.0 / ($clk_per - $wns_setup)}]

puts [format "  Clock        : %s  (period = %.3f ns, target = %.1f MHz)" \
        [get_property NAME $clk_obj] $clk_per [expr 1000.0/$clk_per]]
puts [format "  WNS (setup)  : %+0.3f ns" $wns_setup]
puts [format "  WHS (hold)   : %+0.3f ns" $whs_hold]
puts [format "  Fmax stimata : %.2f MHz" $fmax_mhz]

# Salva il riepilogo sintetico in un file di testo facilmente parsabile
set fp [open "$RPT_DIR/summary.txt" w]
puts $fp "PART=$PART"
puts $fp "TOP=$TOP_MODULE"
puts $fp [format "CLK_PERIOD_NS=%.3f"  $clk_per]
puts $fp [format "WNS_SETUP_NS=%.3f"   $wns_setup]
puts $fp [format "WHS_HOLD_NS=%.3f"    $whs_hold]
puts $fp [format "FMAX_MHZ=%.2f"       $fmax_mhz]
close $fp

puts "\n  Tutti i report sono in: $RPT_DIR/"
puts "  Bitstream:              $OUT_DIR/${PROJ_NAME}.bit"
puts "================================================================================"

