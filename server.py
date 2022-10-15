from flask import Flask, request, jsonify
from datetime import datetime
import heapq
import unittest

app = Flask(__name__)

# global variables
payers = {} # payer name -> Payer
history = [] # heap sorted by time (time,name,points)
payerBalances = {} # payer name -> current balance
usedHistoryEntries= [] # list sorted by time (time,name,transactionPoints), keep around for future extensions

class Payer:
    """
    Class structure for a Payer that has a name, a points balance, and a history of current point transactions 
    """
    def __init__(self,name):
        self.name = name
        self.points = 0 # current total points balance for this payer
        self.transactionAudit = [] # heap history of transactions for this Payer
        
    def addPoints(self,newPoints):
        """
        Adds newPoints to current point balance. If there is a negative balance, resets to 0
        Returns this balance
        """
        self.points += newPoints
        
        if self.getPoints() < 0:
            self.points = 0
        return self.points
    
    def getName(self):
        return self.name
    
    def setPoints(self,newPoints):
        self.points = newPoints
    
    def getPoints(self):
        return self.points
    
    def addTransaction(self,points,dateTime):
        """
        Adds a transaction to the transactionAudit
        """
        heapq.heappush(self.transactionAudit,(dateTime,points))
    
    def removePointsFromEarliestTransaction(self,removePoints):
        """
        Removes points from the earliest transaction from this Payer (used when spending points and this transaction was not fully spent)
        Returns current point balance
        """
        newPoints = self.getPoints() - removePoints
        self.setPoints(newPoints)
        return newPoints        
        
    def removeEarliestTransaction(self):
        """
        Removes earliest transaction for this Payer (used when spending points and this transaction is fully spent)
        """
        heapq.heappop(self.transactionAudit)
        
    def getTransactionAudit(self):
        """
        Returns the sorted transaction audit trail for this Payer
        
        The heap doesn't necessarily exist in sorted form on its own.
        The min sort property is just guaranteed when you pop from it, therefore we need to sort it
        """
        # 
        return sorted(self.transactionAudit)

    
@app.route("/addTransaction", methods=["POST"])
def addTransactionDriver():
    """
    API for receiving a request to add a transaction
    Request has name of payer, dateTime of transaction, and points to add (or subtract)
    Guarantees the Payer balance is never negative
    
    Parses the request, adds a Payer to payers if they do not exist and processes it in addTransactionLogic
    """
    name = request.form["name"]
    points = int(request.form["points"])
    time = datetime.strptime(request.form["timestamp"],"%Y-%m-%dT%H:%M:%SZ") # assumes date is in the format year-month-dateThour:minutes:secondsZ
    
    if name in payers:
        payer = payers[name]
    else:
        payer = Payer(name)
        payers[name] = payer
        
    addTransactionLogic(payer,points,time)

    return 'Request processed'
    
def addTransactionLogic(payer,points,time):
    """    
    Adds the transaction to history, Payer.transactionAudit, updates Payer.points, updates payerBalances
    Guarantees the Payer balance is never negative
    """
    payerName = payer.getName()
    heapq.heappush(history,(time,payerName,points))
    payer.addTransaction(points,time)
    
    currentPoints = 0
    if points >= 0:
        currentPoints = payer.addPoints(points)
    else: 
        if payer.getPoints() != 0: 
            # Removing points with a balance -> need to recalculate as this transaction which
            # may have come earlier than transctions that made current balance
            currentPoints = calculateAndUpdateCurrentPoints(payer)
    
    payerBalances[payerName] = currentPoints
                        
def calculateAndUpdateCurrentPoints(payer):
    """
    Process the in-order transaction audit trail to calculate and update the current balance
    This logic is needed in case the most recent transaction added was out of order and would affect the current balance
    Returns the current balance
    """
    payerHistory = payer.getTransactionAudit()
    newPoints = 0
    
    for transaction in payerHistory:
        points = transaction[1]
        newPoints += points
        if newPoints < 0:
            newPoints = 0
    
    payer.setPoints(newPoints)
    return newPoints

@app.route("/getPayerBalances",methods=["GET"])
def getPayerBalances():
    """
    API for receiving a request to get all current payer balances
    Returns all of the payer balances in the format {"payerName":points}
    """
    return jsonify(payerBalances) 

@app.route("/spendPoints",methods=["POST"])
def spendPointsDriver():
    """
    API for receiving a request to spend a number of points
    Parses request, processes in spendPointsLogic, returns response
    Response is in the format [{"payer":payerName,"points": - spentPoints}]
    """
    points = int(request.form["points"])
    payerSpend = spendPointsLogic(points,history,payers)
    output = []
    
    # format
    for payerName in payerSpend:
        response = {"payer":"","points":0}
        response["payer"] = payerName
        response["points"] = -payerSpend[payerName]
        output.append(response)
    return jsonify(output)
    
def spendPointsLogic(spendPoints,history,payers):
    """
    Spends the amount in spendPoints in chronological order and will not allow negative payer balances
    Updates history, Payer.transactionAudit, Payer.points, payerBalances
    Adds removed/spent transactions to usedHistoryEntries
    
    history and payers are passed in for the unit tests
    """
    payerSpend = {}
    
    while spendPoints and history:
        # get and remove earliest transaction, save it in usedHistoryEntries for future use
        time,name,transactionPoints = heapq.heappop(history)
        usedHistoryEntries.append((time,name,transactionPoints))
        
        payer = payers[name]
        if name not in payerSpend:
            payerSpend[name] = 0
            
        if transactionPoints > 0:
            if transactionPoints <= spendPoints: # using all the points from this transaction
                payerSpend[name] += transactionPoints
                spendPoints -= transactionPoints
                payer.removeEarliestTransaction()
                
            else: # not using all of the points avaliable from this transaction 
                payerSpend[name] += spendPoints     
                currentPoints = payer.removePointsFromEarliestTransaction(spendPoints)
                spendPoints = 0
                heapq.heappush(history,(time,name,currentPoints)) # put back on heap since it's still relevant
                break
        else:
            # use the negative of transactionPoints to make math more logical
            if payerSpend[name] > -transactionPoints:
                payerSpend[name] -= -transactionPoints 
                spendPoints += -transactionPoints
                payerBalances[name] -= -transactionPoints # subtracting from payerSpend at the end is not enough
            else:
                spendPoints += payerSpend[name]
                payerSpend[name] = 0
                payerBalances[name] = 0 # subtracting from payerSpend at the end is not enough
            payer.removeEarliestTransaction()
    
    # update payerBalances and Payer.balance
    for payerName in payerSpend:
        pointsSpent = payerSpend[payerName]
        newBalance = payerBalances[payerName] - pointsSpent
        
        payerBalances[payerName] = newBalance
        payer = payers[payerName]
        payer.setPoints(newBalance)
    
    return payerSpend   

if __name__ == "__main__":
    app.run()