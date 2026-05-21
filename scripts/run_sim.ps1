################################################################################
# File         : scripts/run_sim.ps1
# Descrizione  : Lancia la simulazione behavioral con GHDL.
#                Analizza i sorgenti, elabora il testbench, esegue 200 ns di
#                simulazione e produce:
#                  - sim/build/sim.log      (log testuale con i 'report')
#                  - sim/build/wave.ghw     (waveform GHDL Wave format)
#                  - sim/build/wave.vcd     (waveform VCD universale)
# Uso          :  .\scripts\run_sim.ps1
################################################################################

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

# Aggiunge ghdl al PATH se necessario
if (-not (Get-Command ghdl -ErrorAction SilentlyContinue)) {
    $env:PATH = "$ROOT\tools\bin;$env:PATH"
}

$BUILD = "sim\build"
New-Item -ItemType Directory -Force -Path $BUILD | Out-Null

# Cartella di lavoro per i .o/.cf di GHDL
Push-Location $BUILD

$STD     = "08"                              # VHDL-2008
$WORK    = "work"
$TBNAME  = "tb_hadamard"
$RUNTIME = "200ns"
$VCD     = "wave.vcd"
$GHW     = "wave.ghw"
$LOG     = "sim.log"

$SRC = @(
    "..\..\src\hadamard_core.vhd",
    "..\..\src\hadamard_top.vhd",
    "..\..\sim\tb_hadamard.vhd"
)

Write-Host "================================================================================"
Write-Host "  GHDL simulation flow"
Write-Host "  Standard : VHDL-$STD"
Write-Host "  Top-TB   : $TBNAME"
Write-Host "  Runtime  : $RUNTIME"
Write-Host "================================================================================"

Write-Host "`n--- 1/4 Analyze ---"
foreach ($f in $SRC) {
    Write-Host "  ghdl -a $f"
    ghdl -a --std=$STD --work=$WORK $f
}

Write-Host "`n--- 2/4 Elaborate ---"
ghdl -e --std=$STD --work=$WORK $TBNAME

Write-Host "`n--- 3/4 Run ---"
ghdl -r --std=$STD --work=$WORK $TBNAME `
    --stop-time=$RUNTIME `
    --vcd=$VCD `
    --wave=$GHW 2>&1 | Tee-Object -FilePath $LOG

Write-Host "`n--- 4/4 Summary ---"
$err = (Select-String -Path $LOG -Pattern "FAIL|error" -SimpleMatch -CaseSensitive:$false).Count
$ok  = (Select-String -Path $LOG -Pattern "OK"        -SimpleMatch -CaseSensitive:$true ).Count
Write-Host ("  OK checks  : {0}" -f $ok)
Write-Host ("  FAILures   : {0}" -f $err)
Write-Host ("  VCD file   : {0}\{1}" -f $BUILD, $VCD)
Write-Host ("  GHW file   : {0}\{1}" -f $BUILD, $GHW)
Write-Host ("  Log file   : {0}\{1}" -f $BUILD, $LOG)

Pop-Location

if ($err -gt 0) {
    Write-Host "`nSIMULAZIONE FALLITA" -ForegroundColor Red
    exit 1
} else {
    Write-Host "`nSIMULAZIONE OK" -ForegroundColor Green
}

