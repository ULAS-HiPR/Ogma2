"""Fill every zone of a saved board under its project's own rules, the DRU's included (D-23Nov.30).

    python3 tools/layout/refill.py BOARD.kicad_pcb

KiCad loads a project's custom rules into its DRC engine only when it runs DRC, and only for a board loaded with its
project in a fresh process: so this runs on its own, after the build has saved the board and written the rules
beside it. A fill without the DRU keeps 0.2 mm (the zones' clearance) where the fire rule asks 0.5."""
import sys
import tempfile
import pcbnew as K

if __name__ == '__main__':
    b = K.LoadBoard(sys.argv[1])
    with tempfile.TemporaryDirectory() as tmp:
        K.WriteDRCReport(b, f'{tmp}/drc.rpt', K.EDA_UNITS_MM, False)
    ok = K.ZONE_FILLER(b).Fill(b.Zones())
    K.SaveBoard(sys.argv[1], b)
    print('filled' if ok else 'fill failed')
    sys.exit(0 if ok else 1)
