import numpy as np
from typing import Tuple

class Document():
    '''
    TODO: Add class general description
    '''

    def __init__(self, 
                 **kwargs):
        '''
        Constructor for the Documents object.

        A Document representation is a triple (doc_content, theme_relevance, attribute_usability) where:
        - doc_content: str = the content of the document
        - theme_relevance: np.array = array of the theme relevance scores for a search task consisting of n themes
        - attribute_usability: np.array = array of the attribute usability scores for a search task consisting of m attributes
        '''
        #self.doc_id: int = kwargs.get('doc_id', None)
        self.doc_content: str = kwargs.get('doc_content', None)
        self.theme_relevance: np.array = kwargs.get('theme_relevance', None)
        self.attribute_usability: np.array = kwargs.get('attribute_usability', None)
        #-> assert self.attribute_usability[i] >= 0 and self.attribute_usability[i] <= 1 for i in len(self.attribute_usability), "Attribute Usability must be between 0 and 1"
        self.doc: Tuple = tuple([self.doc_content, self.theme_relevance, self.attribute_usability])
        self.drr: np.array = np.zeros(len(self.theme_relevance))
        self.contrib: float = 0
        self.score: float = 0
        self.crr = np.zeros(len(self.theme_relevance))

    def __str__(self) -> str:
        '''
        Returns the string representation of the Documents object.
        '''

        return f"Document Content {self.doc_content} | Theme Relevance: {self.theme_relevance} | Attribute Usability: {self.attribute_usability} \n\t DRR: {self.drr} | Contribution: {self.contrib} | Score: {self.score}\n"
    
    def set_trels(self, 
                  trels: np.array) -> None:
        '''
        Sets the theme relevance scores for the document.
        '''

        self.theme_relevance = trels
    
    def set_attr(self, 
                 attr: np.array) -> None:
        '''
        Sets the attribute usability scores for the document.
        '''

        self.attribute_usability = attr

    def set_drr(self, 
                drr: np.array) -> None:
        '''
        Sets the cumulated relevance array for the document.
        '''

        self.drr = drr

    def set_contrib(self, 
                    contrib:float) -> None:
        '''
        Sets the cumulated relevance array for the document.
        '''

        self.contrib = contrib

    def set_score(self,
                    score: float) -> None:
            '''
            Sets the score of the document.
            '''
    
            self.score = score

    def set_crr(self,
                crr: np.array) -> None:
        '''
        Sets the cumulated relevance array for the document.
        '''

        self.crr = crr
    
    def attr_fact(self) -> float:
        '''
        Calculates the product of usability factors of a document.
        '''

        return np.prod(self.attribute_usability)