#!/bin/sh

AMS_JOBNAME="system_005_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.1710508883        -1.4580562854        -0.4006572625
        C        -0.6807717226        -1.2946924447        -0.2005531557
        O         0.0962254811        -2.2625949460        -0.1915221118
        N        -0.2534087542         0.0099060045        -0.0261782567
        C        -1.1551882414         1.1851351743        -0.0280913915
        C        -0.1633242284         2.3520582795         0.1844499109
        N         1.1779259903         1.7520904459         0.2977456402
        C         1.0730646302         0.4736726756         0.1750843297
        C         2.2418669185        -0.4496400473         0.2377002028
        H        -2.7291853445        -1.0678292766         0.4634424002
        H        -2.3918675964        -2.5222979448        -0.5284683762
        H        -2.5113492736        -0.9027216750        -1.2872368600
        H        -1.6911245576         1.2545015967        -0.9837795988
        H        -1.8911075940         1.1032746245         0.7826030431
        H        -0.3876061098         2.9229233307         1.0975193376
        H        -0.1758309387         3.0626597852        -0.6551413641
        H         3.1462866185         0.1499101623         0.3915346469
        H         2.1232001926        -1.1717979351         1.0560547690
        H         2.3267411651        -1.0331073662        -0.6881385650
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
