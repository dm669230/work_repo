import paramiko
import pandas as pd

#here i make the function to use paramiko for client and server functionality
def command_run(command):
    # here i gave the credentials for excess
    host = "192.168.8.54"
    username = "debian"
    password = "12345"

    #here i setup the connection to the client
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    _stdin, _stdout,_stderr = client.exec_command(command)

    data=_stdout.read().decode()
    return data
    client.close()

command_id = 'netstat -tuln'        #given the command to the function
data=command_run(command_id)
print(data)
lst=[]

line_data=data.split('\n')      #here i split data in line and further eliment as nested list
line_data.remove(line_data[0])

for i in range(len(line_data)):         
    lst.append(line_data[i].split())

#here i do some manipulation to the data in appropreate format

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
df.to_excel('temp.xlsx', index=False)
