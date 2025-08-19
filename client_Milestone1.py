import socket
import math
import time
import matplotlib.pyplot as plt
import hashlib

client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# client.connect(('vayu.iitd.ac.in',9801))


#The server for now is the localhost. We can change the IP adress for vayu when required
vayuPort = ("127.0.0.1",9801)

#Setting timeout as 0.1 second in case data gets dropped or server doesn't reply
client.settimeout(0.1) 

while True:
    try:
        client.sendto(b"SendSize\nReset\n\n" , vayuPort)
        dataSize = client.recvfrom(1448)
        break
    except socket.timeout:
        print("Sendline request failed")
    

#Slicing received data in order to get the total data size 
dataSize = dataSize[0].decode()
dataSize = dataSize[:-2]
dataSize = dataSize[6:]
dataSize = (int)(dataSize)
print(dataSize)

offset = 0
NumBytes = 1448

#looptime tells us how many unique requests we need to make to the server
looptime = math.ceil(dataSize/NumBytes)
#print(looptime)
finalData = ""



x1 = []
y1 = []
x2 = []
y2 = []

#start time required for plotting graph
start_time = time.perf_counter()

while looptime:
    try:
        num = min(NumBytes, dataSize - offset)
        client.sendto(f"Offset: {offset}\nNumBytes: {num}\n\n".encode() , vayuPort)
        y1.append(offset) 
        end_time = time.perf_counter()
        elapsed_time = end_time -start_time
        x1.append(elapsed_time)
        data = client.recvfrom(4096)
        y2.append(offset) 
        end_time = time.perf_counter()
        elapsed_time = end_time -start_time
        x2.append(elapsed_time)
        data = data[0].decode()
        data = data.split("\n" , 3)

        finalData += data[3]
       # print("added in finalData")
        offset += 1448
        looptime -= 1
    except socket.timeout:
        print("Data dropped. Sending request again...")

ans = hashlib.md5()
ans.update(finalData.encode("utf-8"))
ans = ans.hexdigest()

print(ans)

client.sendto(f"Submit: 2023MCS2481@randomteam\nMD5: {ans}\n\n".encode() , vayuPort)
data = client.recvfrom(2048)

plt.scatter(x1, y1, label= "Request", color= "blue", s=20) 
plt.scatter(x2, y2, label= "Response", color= "orange", s=5) 
  
# x-axis label 

plt.xlabel('Time') 
# frequency label 

plt.ylabel('Offset No.') 
# plot title 

plt.title('UDP request-response') 
# showing legend 
plt.legend() 

plt.grid(True)
plt.savefig('client.png')
plt.show()

print(data)