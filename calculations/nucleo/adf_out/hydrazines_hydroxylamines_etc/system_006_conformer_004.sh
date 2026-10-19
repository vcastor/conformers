#!/bin/sh

AMS_JOBNAME="system_006_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.8319338409         0.4893597839        -0.1698324307
        N         0.5123340813         0.3610191434         0.4654726220
        N        -0.4852751102         0.1052114356        -0.6020848030
        C        -1.8048749643        -0.0231100476         0.0332240189
        H         2.0586164416        -0.3363304835        -0.8697850124
        H         2.5953072064         0.5161500425         0.6193846382
        H         1.8801634125         1.4395140891        -0.7230344832
        H         0.5272215694        -0.5264995341         0.9842547778
        H        -0.5001541354         0.9927221298        -1.1208807647
        H        -2.0315577627         0.8025985100         0.7331557580
        H        -1.8531021385        -0.9732483064         0.5864534654
        H        -2.5682491482        -0.0499246195        -0.7559913773
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
