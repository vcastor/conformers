# -*- coding: UTF-8 -*-
import pandas as pd

def family_classifier(df, region):
    # Every loop restart the category column
    df['category'] = None

    # Assign categories
    if region in ['2', '1']:
        if region == '2':
            df.loc[df['family'] == 'aliphatic_amines', 'category'] = 1
            df.loc[df['family'] != 'aliphatic_amines', 'category'] = 0
        elif region == '1':
            df.loc[df['family'] == 'pyridines_quinolines_etc', 'category'] = 1
            df.loc[df['family'] != 'pyridines_quinolines_etc', 'category'] = 0
    elif region == 'families':
        df['category'] = 0
        df.loc[df['family'] == 'aliphatic_amines', 'category'] = 1
        # df.loc[df['family'] == 'pyridines_quinolines_etc', 'category'] = 2
        # df.loc[df['family'] == 'azoles_and_azole_anions', 'category'] = 3

    return df

