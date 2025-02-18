import pandas as pd
import re
import ir_datasets
import os
from tqdm import tqdm
import time

tqdm.pandas()

from src.mdcu import MDCU
mdcu = MDCU('config/bases.ini')
def matchYear(year):
    match year:
        case "2009":
            qrels = ir_datasets.load('clueweb09/catb/trec-web-2009/diversity')
        case "2010":
            qrels = ir_datasets.load('clueweb09/catb/trec-web-2010/diversity')
        case "2011":
            qrels = ir_datasets.load('clueweb09/catb/trec-web-2011/diversity')
        case "2012":
            qrels = ir_datasets.load('clueweb09/catb/trec-web-2012/diversity')
        case _ :
            raise('Collection for year not found')
    return qrels

t0 = time.time()


base_path_runs = 'private_basePtah' #path to the runs folder
runs_folder_names = ['TREC_18_2009_WebDiversity', 'TREC_19_2010_WebDiversity', 'TREC_20_2011_WebDiversity', 'TREC_21_2012_WebDiversity']

for runs_folder_name in runs_folder_names:
    files = os.listdir(os.path.join(base_path_runs, runs_folder_name, 'runs/catb/'))
    
    prefix = 'input.'
    year = re.search(r'\d{4}', runs_folder_name).group()
    qrels = matchYear(year)
    qrels = pd.DataFrame(qrels.qrels_iter())
    qrels.query_id = qrels.query_id.astype(int)
    
    for file in files:
        if file.startswith(prefix):
            run_name = file[len(prefix):]
            #read run
            try:
                run = pd.read_csv(os.path.join(base_path_runs, runs_folder_name, 'runs/catb/', file), header=None, sep='\t')
                run.columns = ['query_id', 'Q0', 'doc_id', 'rank', 'score', 'run_name']
            except:
                run = pd.read_csv(os.path.join(base_path_runs, runs_folder_name, 'runs/catb/', file), header=None, sep=' ')
                run.columns = ['query_id', 'Q0', 'doc_id', 'rank', 'score', 'run_name']
            run['query_id'] = run['query_id'].astype(int)
            
            
            #set threshold for the number of documents to be considered
            k = 20
            run = run[run['rank'] <= k]

            #run to be fed into mdcu query_id, doc_id, rank, score, run_name
            
            df = mdcu.run_mdcu(run, qrels)
            
            
            if os.makedirs(f'./output/{runs_folder_name}/mdcu_{k}', exist_ok=True):
                df.to_csv(f'./output/{runs_folder_name}/mdcu_{k}/{run_name}.csv', index=False)
            else:
                df.to_csv(f'./output/{runs_folder_name}/mdcu_{k}/{run_name}.csv', index=False)

t1 = time.time()

print(f'Time taken: {t1-t0}')
            
