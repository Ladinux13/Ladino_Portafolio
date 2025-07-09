#############################################################################
##### Welch tests

### Ladino Alvarez Ricardo Arturo

#############################################################################

#### Imports

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import rc
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from itertools import combinations
from statannot import add_stat_annotation


#############################################################################
##### WELCH Plots

def MedErr_graph (Data, Title):

    def formatter(x, pos):
        return str(round(x / 1e6, 1)) + " MDP"

    color = ['#A65E1A','#E9C27D','#B2B2B2','#80CDC1','#018571']

    sns.set(font_scale = 1.5, font="Algerian")
    sns.set_style("white")

    fig = plt.figure (figsize = (16,8), facecolor = "white")

    ax = sns.barplot(x = Data.x,
                     y = Data.y,
                     yerr = Data.yerr,
                     palette = color)
    ax.set(yticks=[Data.y.mean(),  Data.y.max()])
    ax.yaxis.set_tick_params(labelsize = 18)
    ax.yaxis.set_major_formatter(formatter)
    ax.xaxis.label.set_visible(False)
    plt.ylabel(' $\overline{X}_{Price}$',fontsize = 18)
    sns.despine()
    plt.savefig(Title, dpi=300, bbox_inches='tight')


#############################################################################
##### t-TEST & p-VALUE 

def testWelch(Data):

    dp_drup = dict(tuple(Data.drop_duplicates(inplace=False).groupby(Data.columns[0])))

    def t_test(pair):
        results= ttest_ind(dp_drup[pair[0]][Data.columns[-1]],
                           dp_drup[pair[1]][Data.columns[-1]])
        return (results)

    all_combinations = list(combinations(list(dp_drup.keys()), 2))
    t_test = pd.DataFrame([t_test(i) for i in all_combinations])
    Combina = pd.DataFrame(all_combinations, columns =['Ld', 'Jm'])

    New_Data = pd.concat([t_test, Combina], axis=1)

    New_Data = New_Data.replace({1:'01', 2:'02',
                                 3:'03', 4:'04',
                                 5:'05'})

    New_Data = New_Data[['Ld', 'Jm', 'statistic','pvalue']]

    return(New_Data)


#############################################################################
##### WELCH plots (p-VALUES)

def Welch_full (Table, Test, Title):

    def formatter(x, pos):
        return str(round(x / 1e6, 1)) + " MDP"

    color = ['#A65E1A','#E9C27D','#B2B2B2','#80CDC1','#018571']

    sns.set(font_scale = 1, font="Algerian")
    sns.set_style("white")

    fig = plt.figure (figsize = (16,8), facecolor = "white")

    ax = sns.barplot(x = Table.x,
                     y = Table.y,
                     yerr = Table.yerr,
                     palette = color)

    add_stat_annotation(ax,
                        x = Table.x,
                        y = Table.y,
                        order = Table.x,
                        box_pairs = Test[['Ld', 'Jm']].values.tolist(),
                        perform_stat_test = False,
                        pvalues = Test["pvalue"].values.tolist(),
                        test = None,
                        text_format = 'simple',
                        loc='outside',
                        verbose=2);

    ax.yaxis.set_major_formatter(formatter)
    ax.xaxis.label.set_visible(False)
    plt.ylabel(' $\overline{X}_{Price}$')
    plt.title(Title, fontsize = 12)
    sns.despine()
    plt.savefig(Title, dpi=300, bbox_inches='tight')


#############################################################################
##### Uso de la forma de la funcion 
###########################################################################
PRUEBA = pd.read_csv(Entradas + 'TSNE_DEPAS_DEPAS.csv')
DATA, TABLE = Welch_test(PRUEBA, 't_SNE', 'precio')
MedErr_graph(TABLE, 'TITULO SALIDA')
TEST = testWelch(DATA)
Welch_full (TABLE, TEST, 'TITULO SALIDA')
#############################################################################
#############################################################################