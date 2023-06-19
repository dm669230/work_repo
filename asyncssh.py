import asyncssh, sys
import pandas as pd
import asyncio
import os
import time
import logging
import argparse
import nest_asyncio
nest_asyncio.apply()

start_time=time.time()

logging.basicConfig(filename='log_file.log',filemode='w',level=logging.DEBUG, format="%(message)s")  
# logging.getLogger("paramiko.transport").setLevel(logger.CRITICAL)
# logging.getLogger("conn=0").setLevel(logger.CRITICAL)
# logging.getLogger("asyncio").setLevel(logger.CRITICAL)
logging.getLogger("asyncssh").setLevel(logging.WARNING)
logger = logging.getLogger('my_logger')

parser = argparse.ArgumentParser()                      
parser.add_argument('host', help='host address')
parser.add_argument('username', help='username')
parser.add_argument('password', help='password given')

args = parser.parse_args()
ip = str(args.host)
user = str(args.username)
pas = str(args.password)

logger.info("SSH Connection Sucessfull")
directory = os.getcwd() + '\\temp.csv'
print(f"{os.getcwd()}\\temp.csv")
logger.info(directory)
        

async def fun1(conn, start_time1):
        command='cd /home/debian/ion-sfu/examples && ls'
        result1 = await conn.run(command, check=True)
        end_time1=time.time()
        logger.info('\n')
        logger.info(f'first funtion execution time : {end_time1-start_time1}')
        logger.info('\n')
        return result1.stdout

async def fun2(conn, start_time2):
        
        command='netstat -tuln'
        data = await conn.run(command, check=True)
        data=data.stdout
        lst=[]
        line_data=data.split('\n')         #here i split data in line and further eliment as nested list
        line_data.remove(line_data[0])
        for i in range(len(line_data)):         
            lst.append(line_data[i].split())

        #here i do some manipulation in data to get appropreate format
        df = pd.DataFrame(lst)
        df.columns = df.iloc[0]
        df['State']=df['Foreign']
        df = df[1:]
        df['Foreign']=df.iloc[:,[4]]
        df = df.rename(columns={'Local': 'Local Address', 'Foreign': 'Foreign Address'})
        df['Address']
        df=df.drop(df['Address'], axis=1)
        df=df. iloc[:-1,:]
        #covert the data into .xlsx file
        df = pd.DataFrame(df)
        df.to_csv('temp.csv', index=False)
        # logger.warning(data)
        end_time2=time.time()
        logger.info(f"second function execution time :  {end_time2-start_time2}")
        return data

async def run_client() : 
    async with asyncssh.connect(ip, username=user, password=pas) as conn:
        start_time=time.time()
        # =time.time()
        res = await asyncio.gather(fun1(conn, start_time),fun2(conn, start_time))
        end=time.time()
        logger.info(f"time teken by both the function asynchronously : {end-start_time}")

        logger.info(" ")
        logger.info("First Command Data :")
        logger.info(res[0])
        logger.info(" ")

        logger.info("Second Command Data :")
        logger.info(res[1])
        print(res[0],res[1])
        return res
       

try:
    asyncio.get_event_loop().run_until_complete(run_client())
    end_time=time.time()
    logger.info(f"total time teken in this operation : {end_time-start_time}")
    
except Exception as exc:
    print('SSH connection failed: ', exc)