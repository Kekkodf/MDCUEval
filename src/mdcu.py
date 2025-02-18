import math
import numpy as np
import pandas as pd
import os
from typing import List
import configparser
from tqdm import tqdm
tqdm.pandas()

class MDCU:

    def __init__(self, config_file):
        """
        Initialize the MDCU class by reading the base array `b` from the specified config file.

        Args:
            config_file (str): Path to the INI file containing the configuration. The file should have a section called `BaseSettings` with a key `b` containing a comma-separated list of floats.
        """
        self.bases: List[float] = []
        
        # Ensure the config file exists
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"The configuration file '{config_file}' does not exist.")
        
        # Read the INI file
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Extract the base array `b` from the config
        try:
            b_values = config.get("BaseSettings", "b")
            self.bases = [float(x) for x in b_values.split(",")]
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise ValueError(f"Failed to load `b` from config: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid format for `b` in config file. Expected a comma-separated list of floats: {e}")
        
    def __str__(self):
        return f"MDCU(b={[b for b in self.bases]})"
    
    def _contrib(self, matrix, b):
        """
        Calculate the contribution of the computes the contribution of the relevants of the documents retrieved. 

        Args:
            matrix (numpy.ndarray): A matrix of relevance values, where each row represents a document and each column represents a subtopic.
            b (float): The base of the logarithmic discount for the calculation.

        Returns:
            numpy.ndarray: An array containing the contribution of each document.
        """
        
        crr_prime = np.zeros(matrix.shape[1])
        for doc in matrix:
            log = [math.log(crr_prime[i], b) if crr_prime[i] > 0 else 1 for i in range(len(doc))]
            den = [max(1, log[i]) for i in range(len(log))]
            increment = [doc[i] / den[i] for i in range(len(doc))]
            crr_prime += increment
        return crr_prime


    def _mdcu(self, run, qrels, b):
        qrels = qrels.pivot(index=['query_id','doc_id'], columns='subtopic_id', values='relevance').fillna(0)
        
        contribs = []
        for q in run['query_id'].unique():
            try:            
                qrels_per_query = qrels.loc[q]
                qrels_per_query.index.name = 'doc_id'
                #print('qrels_per_query\n', qrels_per_query)

                docs_retrieved = run[run['query_id'] == q]


                filtered = qrels_per_query[qrels_per_query.index.isin(docs_retrieved['doc_id'])]
                doc_themes = filtered.reset_index().melt(id_vars=['doc_id'], var_name='subtopic_id', value_name='relevance')
                #if a relevance is below 0, replace it with 0
                doc_themes.loc[doc_themes['relevance'] < 0, 'relevance'] = 0
                matrix_theme_rel = doc_themes.pivot(index='doc_id', columns='subtopic_id', values='relevance').values

                contrib = self._contrib(matrix_theme_rel, b)
                results_df = pd.DataFrame(data=[(q, contrib, contrib.sum(), b)],
                    columns=['query_id', 'contrib', 'mdcu_score', 'overlap base'])

                contribs.append(results_df)
            except:
                pass

        return pd.concat(contribs).reset_index(drop=True)


    def run_mdcu(self, 
                 run:pd.DataFrame,
                 qrels:pd.DataFrame):   
        results = []
        for b in self.bases:
            results_df = self._mdcu(run, qrels, b)
            results_df['run_name'] = run['run_name'].iloc[0]

            results.append(results_df)
        return pd.concat(results).reset_index(drop=True)
            
            
