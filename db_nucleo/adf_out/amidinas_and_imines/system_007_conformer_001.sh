#!/bin/sh

AMS_JOBNAME="system_007_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         3.6047424288        -0.9648725951         0.1861928045
        N         2.1661222176        -0.9204510081         0.4032464824
        C         1.5085035108        -0.0249835288        -0.2359731143
        C         0.0515304025         0.1473247952        -0.1316218922
        C        -0.5623729026         1.1678101308        -0.8789579266
        C        -1.9434838900         1.3670780365        -0.8104505663
        C        -2.7255948058         0.5465666999         0.0082499723
        C        -2.1211227625        -0.4737676502         0.7574309291
        C        -0.7440682698        -0.6734431327         0.6901776853
        H         3.8830354605        -1.9601648869        -0.1944692350
        H         3.9678356089        -0.1940384256        -0.5191625932
        H         4.1218781173        -0.8417675654         1.1507261293
        H         2.0204214126         0.6868920363        -0.9144151149
        H         0.0526029611         1.8076471379        -1.5174937242
        H        -2.4093368408         2.1624001430        -1.3958972253
        H        -3.8053511155         0.6997197340         0.0648937774
        H        -2.7324747855        -1.1145595904         1.3965891047
        H        -0.2642646389        -1.4638968110         1.2700995332
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
