#!/bin/sh

AMS_JOBNAME="system_009_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -1.4284983942        -1.4527230669         0.4849127162
        C        -1.5879882464        -0.2907530325        -0.3031167734
        C        -0.3193825001         0.1392479462        -1.0322163158
        C         0.8245792811         0.5138278148        -0.0168570601
        O         1.5847019223         1.4351123056        -0.4211730789
        O         0.8614559234        -0.1784032255         1.0401494581
        H        -0.8968698299        -2.2462131603         0.1368540705
        H        -1.7077073467        -1.4717011257         1.4601878053
        H        -2.3227726165        -0.4835838945        -1.1198620314
        H        -2.0080954280         0.5138383002         0.3123990210
        H        -0.5244516665         0.9823425307        -1.7013377939
        H         0.0923993623        -0.6852077846        -1.6368847053
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
