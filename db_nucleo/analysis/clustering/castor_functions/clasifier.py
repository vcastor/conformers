# -*- coding: UTF-8 -*-
import pandas as pd

def reactivity_classifier(df, exp_par, spliter):
    """
    exp_par :: 'experimental_N' or 'experimental_Sn'
    spliter :: [reactive/no-reactive] or [non-reactive/bad/good/very good]
    """
    # Every loop restart the category column
    df['category'] = None

    # Assign categories
    df.loc[df['source'] == 'no_reactive', 'category'] = 'No Reactive'
    df.loc[df['source'] == 'peculiar', 'category'] = 'Peculiar'

    # Quantiles for the spliter only for the reactive ones and not peculiar
    mask_for_quantiles = ((df['source'] != 'peculiar') & (df['source'] != 'no_reactive'))
    q1 = df.loc[mask_for_quantiles, exp_par].quantile(0.25)
    q2 = df.loc[mask_for_quantiles, exp_par].quantile(0.5)
    q3 = df.loc[mask_for_quantiles, exp_par].quantile(0.75)

    if spliter == 'reactive/no-reactive':
        df.loc[(df[exp_par] > 0) & mask_for_quantiles, 'category'] = 'Nucleophile'

        cat_to_num = {
            'No Reactive': 0,
            'Nucleophile': 1,
        }

    elif spliter == 'good/bad':
        df = df[df['source'] != 'no_reactive']
        df = df[df['source'] != 'peculiar']
        df.loc[(df[exp_par] > 0) & (df[exp_par] <= q2) & mask_for_quantiles, 'category'] = 'Bad Nucleophile'
        df.loc[(df[exp_par] > q2) & mask_for_quantiles, 'category'] = 'Good Nucleophile'

        cat_to_num = {
            'Bad Nucleophile': 0,
            'Good Nucleophile': 1,
        }

    else:
        raise ValueError('Invalid spliter value')

    df['category'] = df['category'].map(cat_to_num)

    return df

