import math
import numpy as np
import pandas as pd
from typing import List, Tuple
from src.components import Document

class MDCU():
    '''
    TODO: General Class for MDCU Evaluation
    '''

    def __init__(self, 
                 **kwargs):
        '''
        Constructor for the MDCU object.
        '''
        self.baseOlap: float = kwargs.get('baseOverlap', None)
        self.search_results: List[Document] = kwargs.get('search_results', None)
        self.ideal_results: List[Document] = kwargs.get('ideal_results', None)
    
    def __str__(self) -> str:
        '''
        Returns the string representation of the MDCU object.
        '''
        return f'MDCU framework initialized with base overlap value = {self.baseOlap}.'    
    
    def set_baseOlap(self, 
                     baseOlap: float) -> None:    
        '''
        Sets the base overlap value.
        '''
        self.baseOlap = baseOlap
    

    def set_search_results(self, 
                           search_results: List[Document]) -> None:
        '''
        Sets the search results.
        '''
        self.search_results = search_results

    def set_ideal_results(self, 
                          ideal_results: List[Document]) -> None:
        '''
        Sets the ideal results.
        '''
        self.ideal_results = ideal_results

    def contrib(self,
                crr: np.array, #cumulated relevance array
                documentList: List[Document], #document containing <doc_content, theme_relevance, attribute_usability> = <d.cont, d.trels, d.attr>
                **kwargs) -> None:
        '''
        Contrib function calculates the contribution of a document to the cumulated relevance.

        :param crr: np.array = Initial cumulated relevance array 
        :param documentList: List[Document] = List of documents for wich the contribution is to be calculated
        :return: None
        '''
        
        #compute the contribution of each document
        doc_seen = []
        
        for doc in documentList:
            #compute the attribute factor
            v = doc.attr_fact()
            crr_prime = np.zeros(len(crr))

            #single theme relevance update
            for i in range(len(doc.theme_relevance)):
                log = math.log(crr[i], self.baseOlap) if crr[i] > 0 else 1
                den = max(1, log)
                increment =  doc.theme_relevance[i] / den
                crr_prime[i] = crr[i] + increment
            #print(crr_prime)
                
            #doc.set_crr(crr_prime) # document cumulated relevance update
            doc.set_drr(crr_prime - crr) # document discunted relevance update
            crr = crr_prime #crr update
            prev = doc_seen[-1].score if len(doc_seen) > 0 else 0
            contrib = np.sum(doc.drr)
            doc.set_contrib(contrib)
            score = np.sum(doc.drr) * doc.attr_fact() + prev
            doc.set_score(score)
            doc_seen.append(doc)
            #print(doc)
        return None
    
    def cum_rel(self,
                SearchResults: List[Document],
                **kwargs) -> None:
        '''
        Cum_rel function calculates the rank-wise cumulated relevance with overlap discounts.

        :param SR: List[Document] = List of search results

        :return: None: Updates the cumulated relevance array for each document in the search results and the score
        '''

        #summ all the drrs in the SearchResults
        for doc in SearchResults:
            #set contribution as sum of discunted relevance of themes
            doc.set_contrib(np.sum(doc.drr))
            #set score as contribution * attribute factor
            doc.set_score(doc.contrib * doc.attr_fact())
        
        
                
    def ideal_ranking(self,
                      SearchResults: List[Document],
                      **kwargs) -> List[Document]:
        
        ...


    def run(self,
            SearchResults: List[Document],
            IdealResults: List[Document],
            **kwargs) -> pd.DataFrame:
        '''
        Run function executes the MDCU framework.

        :param SearchResults: List[Document] = List of search results
        :param IdealResults: List[Document] = List of ideal results
        :param task: str = Task to be executed

        :return: None
        '''
        self.contrib(np.zeros(len(SearchResults[0].theme_relevance)), SearchResults)
        self.contrib(np.zeros(len(IdealResults[0].theme_relevance)), IdealResults)
        
        self.cum_rel(SearchResults)
        self.cum_rel(IdealResults)

        self.search_results = SearchResults
        self.ideal_results = IdealResults

        scores_results_obs = []
        docs_seen_search = []
        for doc in self.search_results:
            if len(docs_seen_search) == 0:
                scores = np.array([doc.score])
                docs_seen_search.append(doc.doc_content)
                scores_results_obs.append(scores)
            else:
                scores = np.sum([scores, np.array([doc.score])], axis = 0)
                docs_seen_search.append(doc.doc_content)
                scores_results_obs.append(scores)
        scores_results_obs = np.array(scores_results_obs)
        scores_results_ideal = []
        docs_seen_ideal = []
        for doc in self.ideal_results:
            if len(docs_seen_ideal) == 0:
                scores = np.array([doc.score])
                docs_seen_ideal.append(doc.doc_content)
                scores_results_ideal.append(scores)
            else:
                scores = np.sum([scores, np.array([doc.score])], axis = 0)
                docs_seen_ideal.append(doc.doc_content)
                scores_results_ideal.append(scores)
        scores_results_ideal = np.array(scores_results_ideal)
        
        nmdcu = scores_results_obs / scores_results_ideal
        
        #generate a df with columns doc_content, score, ideal_score, nmdcu
        docs = [doc.doc_content for doc in SearchResults]
        df = pd.DataFrame({'doc_content': docs, 'score': scores_results_obs.flatten(), 'ideal_score': scores_results_ideal.flatten(), 'nmdcu': nmdcu.flatten()})
        #round scores to 2 decimal places
        df['score'] = df['score'].apply(lambda x: round(x, 2))
        df['ideal_score'] = df['ideal_score'].apply(lambda x: round(x, 2))
        df['nmdcu'] = df['nmdcu'].apply(lambda x: round(x, 2))
        return df
        