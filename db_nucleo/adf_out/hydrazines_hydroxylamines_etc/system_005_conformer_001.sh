#!/bin/sh

AMS_JOBNAME="system_005_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.9640755965         0.2075118669        -0.1929219604
        N         0.7762695527        -0.2432006710         0.5397034688
        N        -0.4059746794        -0.1988273305        -0.2957163082
        C        -0.9113137400         1.1736162999        -0.4447240020
        C        -1.4240494826        -1.0437388705         0.3346494816
        H         2.8125583425         0.2044408091         0.5052725884
        H         2.1752658609        -0.5006612769        -1.0055176797
        H         1.8791627341         1.2222207967        -0.6233687176
        H         0.6256351020         0.3968829124         1.3386380530
        H        -1.7977479671         1.1663648064        -1.0935898106
        H        -1.1936100081         1.6161036536         0.5347704974
        H        -0.1502235340         1.8094393724        -0.9144120780
        H        -1.0375159108        -2.0652687770         0.4354781310
        H        -2.3223630627        -1.0567976025        -0.2975910276
        H        -1.7126814117        -0.6704881108         1.3402430296
    End
End

Engine ADF
    TotalEnergy Yes
    Basis
        Type TZP
        Core None
    End
    Symmetry nosym
    XC
       GGA PBE
       DISPERSION Grimme3 BJDAMP
    End
    QTAIM
        AnalysisLevel Full
        Spacing 0.1
    End
    ConceptualDFT
        Enabled YES
        AnalysisLevel Full
    End
    Relativity
        Level None
    End
    NumericalQuality VeryGood
EndEngine

eor
