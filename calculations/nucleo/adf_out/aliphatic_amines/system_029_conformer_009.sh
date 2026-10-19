#!/bin/sh

AMS_JOBNAME="system_029_conformer_009" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.0666273848         0.3110362935        -0.0974247393
        C        -1.0777367622        -0.5798086859        -0.8564985591
        C         0.3314053609        -0.6588994909        -0.2477077426
        N         0.2630439971        -1.2125963816         1.1220901647
        C         1.0831544012         0.6816715793        -0.2741394883
        O         1.3643767510         1.1661731408        -1.6078919373
        H        -1.7350407722         1.3592873834        -0.0547144997
        H        -2.2177575178        -0.0366712925         0.9356100267
        H        -3.0490691624         0.2981236386        -0.5898954629
        H        -0.9928265345        -0.2360123650        -1.9011056384
        H        -1.4750321872        -1.6055439657        -0.9096626928
        H         0.9158607785        -1.3717510348        -0.8531050008
        H         1.2168490171        -1.3046244863         1.4886469002
        H        -0.1883577759        -0.5271398623         1.7387465102
        H         0.5300783663         1.4438881068         0.3034927000
        H         2.0655739449         0.5519085836         0.2021093746
        H         0.5113258477         1.4081063522        -2.0158705119
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
