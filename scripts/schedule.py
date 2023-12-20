import schedule
import time
import scripts.userManagement as userManagement
import scripts.dataBase as db

def updateCurrentWeek():
    userManagement.currentWeek += 1
    db.storeCurrentWeek()

def storeUsers():
    print("hello world")

schedule.every().day.at("00:00").do(updateCurrentWeek)

schedule.every(0.5).minutes.do(storeUsers)


while True:
    schedule.run_pending()
    time.sleep(2)
