#!/bin/sh

AMS_JOBNAME="system_024_conformer_005" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.7572309443         1.7328380292        -0.3147112790
        C        -1.8804621500         0.6346458892        -0.6527745973
        C        -0.9523694206         0.2523841012         0.5059292232
        N         0.0440058547        -0.7749098364         0.1627446696
        C         1.1264335502        -0.3125364882        -0.7291950731
        C         2.2397643586         0.2903059001         0.1264978680
        O         2.5748096473        -0.6273658764         1.1885396339
        H        -3.3440223921         1.4228403191         0.4022256862
        H        -1.2997900908         0.9825335896        -1.5175693690
        H        -2.4674320639        -0.2457571437        -0.9682042533
        H        -0.4248898506         1.1509668795         0.8609343230
        H        -1.5590486124        -0.1189218101         1.3478052341
        H        -0.4265572882        -1.5801994878        -0.2560017954
        H         0.7987912431         0.4217032048        -1.4863533959
        H         1.5162763444        -1.1913234828        -1.2622104667
        H         3.1408152590         0.4646207665        -0.4772428504
        H         1.9187730368         1.2577109000         0.5540603642
        H         1.6914056473        -1.0343673676         1.3833254523
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
