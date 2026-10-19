#!/bin/sh

AMS_JOBNAME="system_041_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.1982820187         0.1993907907         0.6153579732
        C         1.3580680684        -0.7398684781        -0.2566451348
        C         0.0168405856        -0.1405388763        -0.7036224891
        C        -0.9749852314         0.0857479743         0.4432183066
        N        -2.2898718883         0.6305321412         0.0459386130
        H         2.3961865680         1.1475460392         0.0904774525
        H         1.6936616909         0.4422432168         1.5620341801
        H         3.1684566981        -0.2540215738         0.8662827496
        H         1.1684737348        -1.6810056841         0.2887932146
        H         1.9392817873        -1.0170672239        -1.1509274822
        H        -0.4550680257        -0.8099961434        -1.4434694105
        H         0.1963345880         0.8209682451        -1.2183017028
        H        -1.1481281499        -0.8705316593         0.9650862559
        H        -0.5442660273         0.7736701256         1.1869765890
        H        -2.1380088572         1.5229736168        -0.4380449205
        H        -2.6932170055         0.0167519822        -0.6714203628
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
