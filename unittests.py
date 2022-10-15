import unittest
from datetime import datetime
from server import * 
import heapq

class TestAddTransactionLogic(unittest.TestCase):
    
    def test_newPayerAddNegativePointsBalanceNeverNegative(self):
        payer = Payer("Fetch")        
        addTransactionLogic(payer,-200,datetime(2022, 10, 14,0,0,0))
        self.assertEqual(0,payer.getPoints())
    
    def test_normalAdditionToEstablishedPayer(self):
        payer = Payer("Fetch")
        addTransactionLogic(payer,200,datetime(2022, 10, 14,0,0,0))
        addTransactionLogic(payer,300,datetime(2022, 10, 14,0,0,1))        
        self.assertEqual(500,payer.getPoints())
        
    def test_removeTooMuchFromEstablishedPayerBalanceNeverNegative(self):
        payer = Payer("Fetch")
        addTransactionLogic(payer,200,datetime(2022, 10, 14,0,0,0))
        addTransactionLogic(payer,-300,datetime(2022, 10, 14,0,0,1))        
        self.assertEqual(0,payer.getPoints())
        
    def test_negativeBalanceAddedInPast(self):
        payer = Payer("Fetch")
        addTransactionLogic(payer,200,datetime(2022, 10, 14,0,0,0))
        addTransactionLogic(payer,-300,datetime(2022, 10, 12,0,0,1))
        self.assertEqual(200,payer.getPoints())
        
    def test_removeTooMuchInPastThenAddMore(self):
        payer = Payer("Fetch")
        addTransactionLogic(payer,100,datetime(2022, 10, 14,0,0,0))
        addTransactionLogic(payer,500,datetime(2022, 10, 14,0,0,3))          
        self.assertEqual(600,payer.getPoints())
        
        addTransactionLogic(payer,-200,datetime(2022, 10, 14,0,0,1))        
        self.assertEqual(500,payer.getPoints())
        
class TestSpendPointsLogic(unittest.TestCase):
    
    def test_twoPayersWithBalancesThenSpendLessThanTotal(self):
        fetch = Payer("Fetch")
        festival = Payer("Festival")
        payers = {fetch.getName():fetch,festival.getName():festival}
        history = []
        
        heapq.heappush(history,(datetime(2022, 10, 14,0,0,0),fetch.getName(),200))
        addTransactionLogic(fetch,200,datetime(2022, 10, 14,0,0,0))
        
        heapq.heappush(history,(datetime(2022, 10, 14,0,0,5),festival.getName(),400))
        addTransactionLogic(festival,400,datetime(2022, 10, 14,0,0,5))
        
        heapq.heappush(history,(datetime(2022, 10, 14,0,0,6),fetch.getName(),200))
        addTransactionLogic(fetch,200,datetime(2022, 10, 14,0,0,6))
        
        spendPointsLogic(500,history,payers)
        
        self.assertEqual(200,fetch.getPoints())
        self.assertEqual(100,festival.getPoints())
        
    def test_twoPayersWithBalancesThenSpendLessThanTotalAddOutOfOrder(self):
        fetch = Payer("Fetch")
        festival = Payer("Festival")
        payers = {fetch.getName():fetch,festival.getName():festival}
        history = []

        heapq.heappush(history,(datetime(2022, 10, 14,0,0,6),fetch.getName(),200))
        addTransactionLogic(fetch,200,datetime(2022, 10, 14,0,0,6))
        
        heapq.heappush(history,(datetime(2022, 10, 14,0,0,5),festival.getName(),400))
        addTransactionLogic(festival,400,datetime(2022, 10, 14,0,0,5))
        
        heapq.heappush(history,(datetime(2022, 10, 14,0,0,0),fetch.getName(),200))
        addTransactionLogic(fetch,200,datetime(2022, 10, 14,0,0,0))

        spendPointsLogic(500,history,payers)
        
        self.assertEqual(200,fetch.getPoints())
        self.assertEqual(100,festival.getPoints())        
        
    def test_twoPayersWithBalancesThenSpendMoreThanTotal(self):
        fetch = Payer("Fetch")
        festival = Payer("Festival")
        payers = {fetch.getName():fetch,festival.getName():festival}
        history = []
        
        heapq.heappush(history,(datetime(2022, 10, 14,0,0,0),fetch.getName(),200))
        addTransactionLogic(fetch,200,datetime(2022, 10, 14,0,0,0))
        
        heapq.heappush(history,(datetime(2022, 10, 14,0,0,5),festival.getName(),400))
        addTransactionLogic(festival,400,datetime(2022, 10, 14,0,0,5))
        
        heapq.heappush(history,(datetime(2022, 10, 14,0,0,6),fetch.getName(),200))
        addTransactionLogic(fetch,200,datetime(2022, 10, 14,0,0,6))
        
        spendPointsLogic(10000,history,payers)
        
        self.assertEqual(0,fetch.getPoints())
        self.assertEqual(0,festival.getPoints())
                
if __name__ == '__main__':
    unittest.main()