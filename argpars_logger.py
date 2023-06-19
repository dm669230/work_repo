import paramiko
import pandas as pd
import asyncio
import argparse
import logging
import os, time

if __name__ == "__main__":
    
    # here i gave the credentials for excess
    parser = argparse.ArgumentParser()                      
    parser.add_argument('host', help='host address')
    parser.add_argument('username', help='username')
    parser.add_argument('password', help='password given')
    client = paramiko.client.SSHClient() 

    logging.basicConfig(filename='log_file.log',filemode='w',level=logging.DEBUG,format="%(message)s")  
    logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL)
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)

    
    try:

        #here error handling is done whenever correct input is not provided by client
        args = parser.parse_args()
        n1 = str(args.host)
        n2 = str(args.username)
        n3 = str(args.password)
        
        #here i setup the connection to the client
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.connect(n1, username=n2, password=n3)       

        logging.info("SSH Connection Sucessfull")
        directory = os.getcwd() + '\\temp.csv'
        print(f"{os.getcwd()}\\temp.csv")
        logging.info(directory)
        
        async def fun1(start):
            command1 = 'cd /home/debian/ion-sfu/examples && ls'
            _stdin, _stdout,_stderr = client.exec_command(command1)
            data=_stdout.read().decode()
            end=time.time()
            logging.info(f"First Function time : {end-start}")
            return data

        async def fun2(start):
            command2 = 'netstat -tuln'
            _stdin, _stdout,_stderr = client.exec_command(command2)
            data=_stdout.read().decode()
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
            end=time.time()
            logging.info(f"Second Function time : {end-start}")
            return data
        
        async def main():
            start=time.time()
            res = await asyncio.gather(fun1(start),fun2(start))
            end = time.time()
            logging.info(f"time tekken by both the function asynchronously : {end-start}")
            logging.info(" ")
            logging.info("First Command Data :")
            logging.info(res[0])
            logging.info(" ")
            logging.info("Second Command Data :")
            logging.info(res[1])
            return res
            
        asyncio.run(main())
        client.close()
    except Exception as e:
       logging.error('SSH Connection Failed')
       print(e)
    