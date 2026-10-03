from pathlib import Path
import json, re, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, KFold, cross_validate, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED=42
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dataset'/'original'/'netflix_titles.csv'
OUT=ROOT/'dataset'/'processed'
FIG=ROOT/'visualizations'/'week6'

def _parse_duration(value):
    if pd.isna(value): return np.nan
    m=re.search(r'(\d+)',str(value))
    return float(m.group(1)) if m else np.nan

def run_pipeline():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(DATA)
    df=raw.copy()
    df['date_added_parsed']=pd.to_datetime(df['date_added'],errors='coerce')
    df['release_year']=pd.to_numeric(df['release_year'],errors='coerce')
    df['duration_value']=df['duration'].map(_parse_duration)
    df['primary_genre']=df['listed_in'].fillna('Unknown').str.split(',').str[0].str.strip().replace('', 'Unknown')
    df['primary_country']=df['country'].fillna('Unknown').str.split(',').str[0].str.strip().replace('', 'Unknown')
    df['genre_count']=df['listed_in'].fillna('').map(lambda s:len([x for x in s.split(',') if x.strip()]))
    df['country_count']=df['country'].fillna('').map(lambda s:len([x for x in s.split(',') if x.strip()]))
    df['year_added']=df['date_added_parsed'].dt.year
    df['catalogue_delay_years']=df['year_added']-df['release_year']
    exact_dups=int(raw.duplicated().sum())
    # Analysis population needs only a measurable outcome. Preserve original snapshot; do not filter outliers.
    valid=df.dropna(subset=['catalogue_delay_years']).copy()
    negative=int((valid['catalogue_delay_years']<0).sum())
    valid=valid[valid['catalogue_delay_years']>=0].copy()
    valid['catalogue_delay_years']=valid['catalogue_delay_years'].astype(int)
    # retain all nonnegative delays including extreme valid values; split and score with MAE as primary metric.
    features=['type','rating','primary_genre','primary_country','genre_count','country_count','duration_value']
    X=valid[features].copy(); y=valid['catalogue_delay_years'].copy()
    cat=['type','rating','primary_genre','primary_country']
    num=['genre_count','country_count','duration_value']
    prep=ColumnTransformer([('cat',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),('ohe',OneHotEncoder(handle_unknown='ignore',min_frequency=20,sparse_output=False))]),cat),('num',Pipeline([('imputer',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num)])
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=SEED)
    cv=KFold(n_splits=5,shuffle=True,random_state=SEED)
    candidates={
      'Median baseline':DummyRegressor(strategy='median'),
      'Ridge regression':Ridge(alpha=10.0),
      'Random forest':RandomForestRegressor(n_estimators=80,min_samples_leaf=3,max_features=.8,n_jobs=1,random_state=SEED),
      'Histogram gradient boosting':HistGradientBoostingRegressor(max_iter=160,learning_rate=.08,l2_regularization=1.0,random_state=SEED)
    }
    rows=[]; fitted={}
    for name,est in candidates.items():
        pipe=Pipeline([('preprocess',prep),('model',est)])
        scores=cross_validate(pipe,X_train,y_train,cv=cv,scoring={'mae':'neg_mean_absolute_error','rmse':'neg_root_mean_squared_error','r2':'r2'},n_jobs=1)
        pipe.fit(X_train,y_train); pred=pipe.predict(X_test)
        fitted[name]=pipe
        rows.append({'model':name,'cv_mae_mean':-scores['test_mae'].mean(),'cv_mae_sd':scores['test_mae'].std(),'cv_rmse_mean':-scores['test_rmse'].mean(),'cv_r2_mean':scores['test_r2'].mean(),'test_mae':mean_absolute_error(y_test,pred),'test_rmse':mean_squared_error(y_test,pred)**.5,'test_r2':r2_score(y_test,pred)})
    comp=pd.DataFrame(rows).sort_values('cv_mae_mean').reset_index(drop=True)
    comp.to_csv(OUT/'week6_model_comparison.csv',index=False)
    selected_name=comp.iloc[0]['model']; selected=fitted[selected_name]; pred=selected.predict(X_test)
    metrics={'dataset':'Netflix Movies and TV Shows by Shivam Bansal (Kaggle snapshot)','source':'https://www.kaggle.com/datasets/shivamb/netflix-shows','access_date':'2026-10-03','raw_rows':len(raw),'raw_columns':len(raw.columns),'exact_duplicate_rows':exact_dups,'missing_date_added_rows':int(df['date_added_parsed'].isna().sum()),'missing_release_year_rows':int(df['release_year'].isna().sum()),'negative_delay_rows_excluded':negative,'analysis_rows':len(valid),'test_rows':len(y_test),'features':features,'target':'catalogue_delay_years = year(date_added) - release_year','target_note':'Approximate time gap in whole years; not a licensing duration or causal outcome. year_added and release_year excluded from predictors.','split':{'test_size':.2,'random_state':SEED,'cv':'5-fold shuffled KFold on training split'},'models':comp.to_dict(orient='records'),'selected_model':selected_name,'test_actual_delay_median':float(y_test.median()),'test_actual_delay_mean':float(y_test.mean()),'test_actual_delay_p90':float(y_test.quantile(.9)),'test_prediction_median':float(np.median(pred)),'test_mae':float(mean_absolute_error(y_test,pred)),'test_rmse':float(mean_squared_error(y_test,pred)**.5),'test_r2':float(r2_score(y_test,pred)),'interpretation':'Associational estimation on one Netflix catalogue snapshot. Does not measure licensing negotiations, audience response, or causal determinants.'}
    (OUT/'week6_model_results.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    analysis={'raw_shape':list(raw.shape),'missing_by_column':raw.isna().sum().astype(int).to_dict(),'duplicate_rows':exact_dups,'type_counts':raw['type'].value_counts().to_dict(),'rating_counts':raw['rating'].fillna('Missing').value_counts().head(12).to_dict(),'valid_delay_rows':len(valid),'delay_describe':y.describe(percentiles=[.25,.5,.75,.9,.95]).to_dict(),'negative_delay_rows':negative,'date_added_missing':metrics['missing_date_added_rows']}
    (OUT/'week6_data_quality.json').write_text(json.dumps(analysis,indent=2,default=float),encoding='utf-8')
    valid[['show_id','type','release_year','date_added','catalogue_delay_years']+features[1:]].to_csv(OUT/'week6_analysis_data.csv',index=False)
    # EDA charts
    sns.set_theme(style='whitegrid',palette='deep')
    fig,ax=plt.subplots(figsize=(9,5)); sns.histplot(valid['catalogue_delay_years'],bins=45,ax=ax,color='#277da1'); ax.set(xlabel='Approximate catalogue delay (years)',ylabel='Titles',title='Catalogue delay distribution'); fig.tight_layout(); fig.savefig(FIG/'delay_distribution.png',dpi=180); plt.close(fig)
    top=valid['primary_genre'].value_counts().head(12).index
    group=valid[valid.primary_genre.isin(top)]
    fig,ax=plt.subplots(figsize=(11,6)); sns.boxplot(data=group,x='catalogue_delay_years',y='primary_genre',order=group.groupby('primary_genre').catalogue_delay_years.median().sort_values().index,showfliers=False,ax=ax,color='#90be6d'); ax.set(xlabel='Approximate delay (years; outliers hidden for readability)',ylabel='Primary listed genre',title='Catalogue delay across common primary genres'); fig.tight_layout(); fig.savefig(FIG/'delay_by_genre.png',dpi=180); plt.close(fig)
    yearly=valid.groupby('year_added').agg(titles=('show_id','size'),median_delay=('catalogue_delay_years','median')).reset_index()
    fig,ax=plt.subplots(figsize=(10,5)); sns.lineplot(data=yearly,x='year_added',y='titles',marker='o',ax=ax,color='#277da1'); ax.set(xlabel='Year added (snapshot field)',ylabel='Titles in dataset',title='Recorded catalogue additions by year'); fig.tight_layout(); fig.savefig(FIG/'additions_by_year.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5)); sns.barplot(data=comp,x='test_mae',y='model',ax=ax,color='#f9c74f'); ax.set(xlabel='Held-out mean absolute error (years)',ylabel='',title='Model comparison on held-out test set'); fig.tight_layout(); fig.savefig(FIG/'model_comparison.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,5)); ax.scatter(y_test,pred,s=12,alpha=.25,color='#277da1'); lim=max(float(y_test.quantile(.99)),float(np.quantile(pred,.99))); ax.plot([0,lim],[0,lim],'--',color='#f94144'); ax.set(xlim=(0,lim),ylim=(0,lim),xlabel='Observed delay (years)',ylabel='Estimated delay (years)',title='Observed and estimated delay (99th percentile range)'); fig.tight_layout(); fig.savefig(FIG/'observed_vs_estimated.png',dpi=180); plt.close(fig)
    return metrics,analysis,comp

if __name__=='__main__':
    m,a,c=run_pipeline(); print(json.dumps({'analysis_rows':m['analysis_rows'],'selected_model':m['selected_model'],'test_mae':m['test_mae'],'test_rmse':m['test_rmse'],'test_r2':m['test_r2'],'delay_summary':a['delay_describe']},indent=2,default=float))
