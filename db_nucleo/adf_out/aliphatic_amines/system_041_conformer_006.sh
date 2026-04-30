#!/bin/sh

AMS_JOBNAME="system_041_conformer_006" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.2078576266         0.2202762456         0.5413521314
        C         1.3719018120        -0.8067388041        -0.2298793578
        C         0.0327022456        -0.2682067572        -0.7505429887
        C        -0.9613795980         0.0955056971         0.3507642311
        N        -2.2670575715         0.4801427849        -0.2308527835
        H         3.1796417566        -0.2028852230         0.8363302878
        H         2.4028950505         1.1109036275        -0.0773380644
        H         1.7012861659         0.5555433303         1.4583063517
        H         1.9580203710        -1.1755397840        -1.0871560446
        H         1.1815928789        -1.6848708930         0.4118718524
        H         0.2161451468         0.6233474757        -1.3786754861
        H        -0.4379090019        -1.0208142856        -1.4050474947
        H        -1.1256040301        -0.7840365307         0.9958378103
        H        -0.5355604498         0.8882762441         0.9935327637
        H        -2.1360708369         1.3394863957        -0.7772070147
        H        -2.8964210111         0.7564049696         0.5304376376
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
