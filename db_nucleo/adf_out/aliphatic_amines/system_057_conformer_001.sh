#!/bin/sh

AMS_JOBNAME="system_057_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O         2.4249972712        -0.5701585238        -0.2824374956
        C         1.5518373578         0.4373019014         0.2601638824
        C         0.2280450472         0.4592405848        -0.5064796839
        C        -0.8399293881         1.3511430874         0.1869633455
        C        -2.0315032197         0.4053469515         0.4457266442
        C        -1.3694128370        -0.9786445015         0.4928022817
        N        -0.3030294555        -0.9375407206        -0.5386359343
        H         1.7898042939        -1.3022059891        -0.4800652921
        H         2.0633620028         1.4073744989         0.1834891825
        H         1.3548575832         0.2343027894         1.3301232103
        H         0.4275401361         0.7775737719        -1.5400524943
        H        -1.1165803908         2.2140853417        -0.4321463102
        H        -0.4430637804         1.7399932105         1.1384368021
        H        -2.5808973194         0.6544945516         1.3646192187
        H        -2.7407508116         0.4441778047        -0.3957449480
        H        -2.0572314018        -1.8111801751         0.2948543391
        H        -0.9066580327        -1.1492652212         1.4782419370
        H        -0.7471974209        -1.0825407934        -1.4496761448
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
