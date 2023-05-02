from DownloadCSV import download
from Compute import generateNewestIronConorsEV

def all():
    download("BearCall", "https://www.barchart.com/options/call-spreads/bear-call?orderBy=maxProfitPercent&orderDir=desc")
    download("BullPut", "https://www.barchart.com/options/put-spreads/bull-put?orderBy=maxProfitPercent&orderDir=desc")
    download("IronCon", "https://www.barchart.com/options/short-condors?orderBy=breakEvenProbability&orderDir=desc")
    
    #analyze data 
    generateNewestIronConorsEV("BearCall")
    generateNewestIronConorsEV("BullPut")
    generateNewestIronConorsEV("IronCon")

all()