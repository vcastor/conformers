#!/bin/sh

AMS_JOBNAME="system_009_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -2.2905774354        -1.1225372045        -0.5286766472
        C        -1.3101975328        -0.4574740124         0.2645483960
        C        -0.0923139295        -0.1606487131        -0.6463196030
        C         1.0364899434         0.6401423828         0.1672237674
        O         0.7427753370         1.0944764233         1.2897114849
        O         2.0854561134         0.6823816978        -0.5320044527
        H        -2.7396767946        -0.5897479730        -1.2734964219
        H        -2.1366984461        -2.1040616830        -0.7573884823
        H        -1.0052804607        -1.0958927511         1.1012825966
        H        -1.7047808526         0.4921080223         0.6481931151
        H         0.3537975318        -1.0834462737        -1.0357833632
        H        -0.3716230132         0.4804836921        -1.4942350777
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
