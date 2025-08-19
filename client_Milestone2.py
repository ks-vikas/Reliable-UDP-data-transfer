import socket
import math
import time
import matplotlib.pyplot as plt
import hashlib

client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
vayuPort = ("10.17.7.134",9801)


#The server for now is the localhost. We can change the IP adress for vayu when required
# vayuPort = ("127.0.0.1",9801)

#Setting timeout as 0.1 second in case data gets dropped or server doesn't reply
client.settimeout(0.02) 

window_size = 10

while True:
    try:
        client.sendto(b"SendSize\nReset\n\n" , vayuPort)
        dataSize = client.recvfrom(4096)
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

keys = range(0, dataSize, 1448) 

dic = {key: "" for key in keys}

#looptime tells us how many unique requests we need to make to the server
#looptime = math.ceil(dataSize/NumBytes)

remaining_offset = list(keys)

data_received = 0
data_squished = False
#optimal_window = window_size


x1 = []
y1 = []
x2 = []
y2 = []
squished = []
burst = []
xtime = []

#start time required for plotting graph
start_time = time.perf_counter()

def receive():
    global window_size
    global remaining_offset
    global data_squished
    data = client.recvfrom(4096)
    data = data[0].decode()
    data = data.split("\n" , 3)

    cur_offset = int(data[0][8:])

    y2.append(cur_offset) 
    end_time = time.perf_counter()
    elapsed_time = end_time -start_time
    x2.append(elapsed_time)

    xtime.append(elapsed_time)
    if data[2] == "Squished":
        data_squished = True
        dic[cur_offset] = data[3][1:]
        print("SQUISHEDDD")
        squished.append(1)
    else:    
        dic[cur_offset] = data[3]
        squished.append(0)
    remaining_offset.remove(cur_offset)
    burst.append(window_size)

while len(remaining_offset) > 0:
    for i in range(0,min(window_size, len(remaining_offset)),1):
        num = min(NumBytes, dataSize - remaining_offset[i])
        client.sendto(f"Offset: {remaining_offset[i]}\nNumBytes: {num}\n\n".encode() , vayuPort)
        y1.append(remaining_offset[i]) 
        end_time = time.perf_counter()
        elapsed_time = end_time -start_time
        x1.append(elapsed_time)
        time.sleep(0.005)

    for i in range(0,min(window_size, len(remaining_offset))):
        try:
            receive()
            data_received += 1
            print("received")
            print(remaining_offset)
        except socket.timeout:
            print("timeout")
        
    # if (window_size > data_received) or data_squished:
    #     data_squished = False
    #     window_size = window_size//2
    # else:
    #     #optimal_window = window_size
    #     window_size += 1
    
finalData = ""
for data in dic.values():
    finalData += data


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

plt.scatter(xtime, squished, label= "Squished", color= "orange", s=10) 

plt.xlabel('Time') 

plt.ylabel('Squished') 

plt.grid(True)

plt.savefig('client1.png')
print("Burst Size = 10 , Timeout: 0.02 , sleep timer = 0.005")
print(data)