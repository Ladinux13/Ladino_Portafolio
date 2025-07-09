#############################################################################
##### OUTLIER DETECTION
##### LOCAL OUTLIER FACTOR (LOF)

### Ladino Álvarez Ricardo Arturo
#############################################################################

#### Librerias base

import numpy as np
import pandas as pd
import geopandas as gpd

import warnings
warnings.filterwarnings('ignore')

### OUTLIER

from sklearn.neighbors import LocalOutlierFactor

#############################################################################
#####  Apartment Outliers

DEPAS_VENTA = INMUEBLES[INMUEBLES['Oferta'].isin(['Departamento'])]

CLF_DEPA = LocalOutlierFactor( n_neighbors = 300,
                               contamination ='auto')

X_DEPA = DEPAS_VENTA[['precio','superficie','habitacion','baños']].values

Y_DEPA = CLF_DEPA.fit_predict(X_DEPA)

DF_DEPA= pd.DataFrame(Y_DEPA, columns=['outlier'])

OUTLIER_DEPA = pd.DataFrame(DEPAS_VENTA[[ 'id','precio',
                                          'superficie','habitacion',
                                          'baños']])

OUTLIER_DEPA['Outlier'] = DF_DEPA.values

OUTLIER_DEPA = OUTLIER_DEPA.query('Outlier == 1')

OUT_LIED = DEPAS_VENTA.merge( OUTLIER_DEPA[['id','Outlier']],
                              left_on = 'id',
                              right_on = 'id',
                              how ='right')

OUT_LIED = OUT_LIED.to_crs(6372)

##### Assign hex code

HEX_DPTO = gpd.sjoin( HEX_CDMX,
                      OUT_LIED,
                      how="right",
                      op='contains')

HEX_DPTO = HEX_DPTO[HEX_DPTO['hex'].notna()]

HEX_DPTO = HEX_DPTO.drop([ 'index_left', 'Outlier',
                           'geometry'], axis=1)


#############################################################################

### DEPARTAMENTOS
HEX_DPTO.to_csv(Salidas + "DEPAS_EN_VENTA.csv", index = False)
