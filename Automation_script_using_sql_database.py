import pandas as pd
import re
import asyncio
# from dbconnection import connection
import mysql.connector
from mysql.connector import Error

connection = mysql.connector.connect(
    host='127.0.0.1', 
    user='root',
    password='mysql',
    database='volte_dashboard_dummy',
)

# Read VOLTE_mp data from Excel
excel_data_mp = pd.read_excel("MPC Nokia VOLTE_Mp' Interface.xlsx", "Alarm for Mp' interface")

# Extract node data for VOLTE_mp
async def node_data_mp(dataframe_mp):
    data_list_mp = []
    
    dn_pattern = r"NTAS-(.*?)/SERVICE"
    supp_pattern = r'SA {"mgw_id": (.*?);'

    for index, row in dataframe_mp.iterrows():
        alarm_Supp = row['SUPPLEMENTARY_INFO']
        alarm_DN = row['DN']
        database = {}

        # Extract A side node information
        matchDN = re.search(dn_pattern, alarm_DN)
        database["A_side_Node"] = matchDN.group(1)

        # Extract B side node information
        matchSUPP = re.search(supp_pattern, alarm_Supp)
        database["B_Side_node"] = matchSUPP.group(1)
        data_list_mp.append(database)

    return data_list_mp

# Filter VOLTE_mp data based on alarm number
dataframe_mp = excel_data_mp[excel_data_mp['ALARM_NUMBER'] == 160233]


# Read VOLTE_RX data from Excel
excel_data_rx = pd.read_excel('MPC Nokia VOLTE_Rx Interface.xlsx', "Alarm as per Alarm Report")

# Extract node data for VOLTE_RX
async def node_data_rx(dataframe_rx):
    data_list_rx = []
    dn_pattern = r'71.233.26;Remote FQDN: (.*?);Remote'
    supp_pattern = r'LSS_diamLinkDown: Local IP address: (.*?);Remote'

    for index, row in dataframe_rx.iterrows():
        alarm_Supp = row['TEXT']
        alarm_DN = row['SUPPLEMENTARY_INFO']
        database = {}

        # Extract A end PRI IP
        matchSUPP = re.search(supp_pattern, alarm_Supp)
        database["A_end_PRI_IP"] = matchSUPP.group(1)

        # Extract B end PRI IP
        matchDN = re.search(dn_pattern, alarm_DN)
        database["B_end_PRI_IP"] = matchDN.group(1)

        data_list_rx.append(database)

    return data_list_rx

# Filter VOLTE_RX data based on alarm number
dataframe_rx = excel_data_rx[excel_data_rx['ALARM_NUMBER'] == 10129]


# Read VOLTE_SH data from Excel
excel_data_sh = pd.read_excel('MPC Nokia VOLTE_Sh Interface.xlsx', "Alarm For Sh")

# Extract node data for VOLTE_SH
async def node_data_sh(dataframe_sh):
    data_list_sh = []
    local_ip_pattern = r'Local IP address: (.*?); Second'
    second_local_ip_pattern = r' Second Local IP address: (.*?) Remote FQDN'
    remote_ip_pattern = r'Remote IP address: (.*?); Second Remote'
    second_remote_ip_pattern = r'Second Remote IP address: (.*?); Port'

    for index, row in dataframe_sh.iterrows():
        alarm_data = row['SUPPLEMENTARY_INFO']
        database = {}

        # A end PRI IP
        matchDN1 = re.search(local_ip_pattern, alarm_data)
        database["A_end_PRI_IP"] = matchDN1.group(1)

        # A end SEC IP
        matchDN2 = re.search(second_local_ip_pattern, alarm_data)
        database["A_end_SEC_IP"] = matchDN2.group(1)

        # B end PRI IP
        matchDN3 = re.search(remote_ip_pattern, alarm_data)
        database["B_end_PRI_IP"] = matchDN3.group(1)

        # B end SEC IP
        matchDN4 = re.search(second_remote_ip_pattern, alarm_data)
        database["B_end_SEC_IP"] = matchDN4.group(1)

        data_list_sh.append(database)

    return data_list_sh

# Filter VOLTE_SH data based on alarm number
dataframe_sh = excel_data_sh[excel_data_sh['ALARM_NUMBER'] == 160610]


# Read VOLTE_SIGTRAN data from Excel
excel_data_sig = pd.read_excel('MPC Nokia VOLTE_SIGRAN interface.xlsx', "Alarm for SIGTRAN")

# Extract node data for VOLTE_SIGTRAN
async def node_data_sigtran(dataframe_sig):
    supp_pattern = r'IMPACT:SA {"SP_CODE": (.*?);'
    dn_pattern = r"NTAS-(.*?)/SERVICE"
    data_list_sigtran = []

    for index, row in dataframe_sig.iterrows():
        alarm_Supp = row['SUPPLEMENTARY_INFO']
        alarm_DN = row['DN']
        database = {}

        # Extract A side node information
        matchDN = re.search(dn_pattern, alarm_DN)
        database["A_side_Node"] = matchDN.group(1)
        
        # Extract B side node information
        matchSUPP = re.search(supp_pattern, alarm_Supp)
        database["B_Side_node"] = matchSUPP.group(1)


        data_list_sigtran.append(database)

    return data_list_sigtran

# Filter VOLTE_SIGTRAN data based on alarm number
dataframe_sig = excel_data_sig[excel_data_sig['ALARM_NUMBER'] == 160102]


async def main():
    result_mp, result_rx, result_sh, result_sig = await asyncio.gather(
        node_data_mp(dataframe_mp),
        node_data_rx(dataframe_rx),
        node_data_sh(dataframe_sh),
        node_data_sigtran(dataframe_sig)
    )
    
    cursor = connection.cursor()
    cursor.execute('UPDATE volte_links SET alarmStat = 0')
    
    for i in range(max(len(result_mp), len(result_rx), len(result_sh), len(result_sig))):
        try:
            # Updation queries for VOLTE_SH, VOLTE_RX, VOLTE_mp, VOLTE_SIGTRAN
            query_mp = f"UPDATE volte_links SET alarmStat = 1 WHERE A_side_Node = '{result_mp[i]['A_side_Node']}' AND B_Side_node LIKE '%{result_mp[i]['B_Side_node']}%'"
            query_rx = f"UPDATE volte_links SET alarmStat = 1 WHERE A_end_PRI_IP = '{result_rx[i]['A_end_PRI_IP']}' AND B_end_PRI_IP = '{result_rx[i]['B_end_PRI_IP']}'"            
            query_sh = f"UPDATE volte_links SET alarmStat = 1 WHERE A_end_PRI_IP = '{result_sh[i]['A_end_PRI_IP']}' AND A_end_SEC_IP = '{result_sh[i]['A_end_SEC_IP']}' AND B_end_PRI_IP = '{result_sh[i]['B_end_PRI_IP']}' AND B_end_SEC_IP = '{result_sh[i]['B_end_SEC_IP']}'"
            query_sigtran = f"UPDATE volte_links SET alarmStat = 1 WHERE A_side_Node = '{result_sig[i]['A_side_Node']}' AND B_Side_node LIKE '%{result_sig[i]['B_Side_node']}%'"

            # Execute the queries
            if query_sh:
                cursor.execute(query_sh)

            if query_mp:
                cursor.execute(query_mp)

            if query_rx:
                cursor.execute(query_rx)

            if query_sigtran:
                cursor.execute(query_sigtran)

            # Commit the changes
            connection.commit()
            print("Final Data Updated successfully.")
            print(result_mp,result_rx,result_sh,result_sig)
            # Close the connection to the MySQL database
            connection.close()

        except Error as e:
            print("Error accessing data in MySQL:", e)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
