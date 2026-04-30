#!/bin/sh

AMS_JOBNAME="system_006_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.1508752207        -1.5263338496        -0.4660488978
        N        -1.6106230318        -0.2051476675        -0.1622323564
        C        -2.5231788813         0.8667180794         0.2242121493
        C        -0.2622073902        -0.0295389486        -0.0414522067
        C         0.3064338067         1.2142034984         0.3451794846
        C         1.6867035022         1.3410877426         0.4265852515
        N         2.5754151001         0.3521410057         0.1747510433
        C         2.0250161338        -0.8325473369        -0.1781185407
        C         0.6633854511        -1.0776435646        -0.2956256643
        H        -1.9380665166        -2.2530098419         0.3366291655
        H        -1.7329770417        -1.9149417117        -1.4071277422
        H        -3.2355254279        -1.4453374155        -0.5838044203
        H        -2.3280224504         1.7797763399        -0.3585855333
        H        -2.4370346506         1.1121379003         1.2963778374
        H        -3.5495147906         0.5456776919         0.0221671887
        H        -0.3184533853         2.0748722937         0.5799196167
        H         2.1120291653         2.3053118503         0.7231191378
        H         2.7277605494        -1.6476215064        -0.3791908908
        H         0.3282430682        -2.0745485998        -0.5789978387
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
