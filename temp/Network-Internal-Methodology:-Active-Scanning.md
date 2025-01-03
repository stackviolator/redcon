## [[https://github.ibm.com/X-Force-Red/Testing-Methodology/blob/master/icons/icons8-info-50.png]] About

This page describes performing unauthenticated reconnaissance by port scanning TCP and UDP. Port-scanning hosts allows for enumeration of available services (open TCP and UDP ports). 


Tags: \#redteaming \#netpen \#recon \#nmap \#masscan \#portscan \#tcp \#udp \#icmp

## [[https://github.ibm.com/X-Force-Red/Testing-Methodology/blob/master/icons/icons8-catapult-50.png]] How To

Follow the links below for detailed technique/command guidance.

Link to Tool | What's it do? | Where do you run it? | Requires creds? | Notes
--- | --- | --- | --- | --- 
[Nmap](https://nmap.org/book/man.html) | Network Mapper | Attacker machine | None | ICMP/Port scan activity may trigger alerts on generic IDP/IPS default deployments. Lowering scan timing will avoid detection in most cases
[masscan](https://github.com/robertdavidgraham/masscan) | Network Mapper | Attacker machine | None | Scanning at a rate higher than `--rate=4000` pps may result in inconsistent results, open server ports not be discovered, etc. By default Masscan randomizes targets `-n -Pn --randomize-hosts` so not to overload servers being scanned.
[monkiirobot.rb](https://github.ibm.com/Piotr-Marszalik/monkiirobot) | Network Mapper - Parser | Attacker machine | None | Simple tool to automate common unauthenticated discovery scans during network reconnaissance and parse results into useful formats. 
PowerShell |  | Target machine | None | Examples of tcp and udp port-scanning using PowerShell and one-liners. 



### Nmap
* `nmap -Pn -n --open -p 53,88,135,137,139,445,389,636,3389,5985 <ip>` 
	* An example command for running against single target. ICMP check is disabled (-Pn) meaning port scan will continue even if hosts have ping disabled. The (-n) flag disables DNS resolv during scans, which makes large scans complete faster. The (--open) will only show OPEN ports (suppresses inaccessible 'filtered' ports). The default is TCP Syn (-sS), in above example targeting common ports related to Windows Active Directory management (88,135,137,139,445,389,636,3389,5985)
* `nmap -Pn -n --open -p 21,22,53,111,2049,69,161,5900,88,135,137,139,445,389,636,3389,5985,80,443,8080,8443,1433,3306 -iL <ip ranges file> -oA <results-tcp-sample-fast> `
	* Example command of using nmap to run port scan (common ports of interest) against targets from a file, and outputing results in all formats (.xml, .gnmap, .nmap)
* Nmap discovery scan of common Windows ports only can be automated using `monkiirobot.rb` tool, use the following command:
 	* `sudo ruby monkiirobot.rb nmap-winfast`

Resuming Scans
* Nmap has the ability to resume a scan if it needs to be stopped due to a client time window, failure or etc.
* Conditions/Limitations:
  * Scan should be stopped with ctrl-c to properly be resumed, but there is a chance it will work if some output was written.
  * Output must have been written to Grepable or Nmap format (if you used our default of -oA outputting to all formats you are good).
  * The --open and --randomize-hosts options cannot be used. 
  * Hosts partially scanned will be fully rescanned when resuming.
* Syntax:
  * ```nmap --resume <.nmap or .gnmap file to resume from>```
* Example:
  * ```nmap --resume TCP_AllPorts_sS_T1.nmap```

TCP lites
* `nmap -iL subnets.txt -Pn -O --osscan-limit -sS -sV --top-ports 300 --defeat-rst-ratelimit --open -T4 --script=resolveall,reverse-index --script-args http.useragent="Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko" --script-timeout 500m --stats-every 240s --host-timeout 1080m --randomize-hosts -oA TCP_Top300Ports_sS_sV`
	* Top 300 TCP ports for initial targeting
		* Above scan includes performing service versioning across identified open ports and Operating System detection (OS detection fingerprint is best effort and may be inaccurate)
		Consider also SMB OS Discovery
			* `nmap --script smb-os-discovery -p445 -iL subnets.txt -n -Pn`
			* `nmap --script smb-os-discovery -p445 -iL subnets.txt --open -n -Pn -oA subnets_OS_discovery445`
				remove (-n) to DNS resolve hostnames
* `screen -dmS screenTLite bash -c ' sudo nmap -Pn -O --osscan-limit -sS -sV --top-ports 2000 --defeat-rst-ratelimit --open -T4 --script=resolveall,reverse-index --script-args http.useragent="Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko" --script-timeout 500m --stats-every 240s --host-timeout 1080m --randomize-hosts -iL ips.txt -oA TCP_Top2ksV   '`
    * start in screen lite TCP top 2000
* To check which ports are scanned with top-ports command:
 	* `nmap --top-ports 2000 localhost -v -oG - `

* Nmap discovery scan of top 300 most common TCP ports or top 2000 most common TCP ports can be automated using `monkiirobot.rb` tool, use the following commands: 
 	* `sudo ruby monkiirobot.rb nmap-tcplite-top300 `
 	* `sudo ruby monkiirobot.rb nmap-tcplite-top2k`





UDP lites
* `nmap -iL subnets.txt -Pn -sU -sV --top-ports 500 -T3 --defeat-icmp-ratelimit --script=reverse-index --script-timeout 500m --stats-every 240s --host-timeout 1080m -oA UDP_Top500Ports_sU_sV `
	* Top 500 UDP ports for initial targeting
* `screen -dmS screenULite bash -c ' sudo nmap -iL ips.txt  -Pn -sU -sV --top-ports 500 -T3 --defeat-icmp-ratelimit --script=reverse-index --script-timeout 500m --stats-every 240s --host-timeout 1080m -oA UDP_Top500sUsV  '`
    * start in screen
* Nmap discovery scan of top 200 most common UDP ports can be automated using `monkiirobot.rb` tool, use the following command: 
 	* `sudo ruby monkiirobot.rb nmap-udplite-top200 `




TCP fulls
* `nmap -Pn -n --open -p- -iL <targets.txt> -oA <output-TCP-full.xml>`
	* example command to run TCP port scan against all available ports (1-65535)
* `screen -dmS screenTFull bash -c ' sudo nmap -Pn -n --open -T4 -p- -iL ips.txt -oA fullTCP  ' `
    * full TCP start in screen
* `sudo nmap 10.1.1.0/24 -n -Pn -p- --defeat-rst-ratelimit --open -T4 --randomize-hosts  -oA out-full1`
	* example full range TCP scan, output to file in all formats
* `screen -dmS screen-full1 bash -c 'sudo nmap 10.1.1.0/24 -n -Pn -p- --defeat-rst-ratelimit --open -T4 --randomize-hosts  -oA out-full1 ' `
	* example to start scan in screen, non interactive deamon


* `nmap -iL targets.txt -Pn -O --osscan-limit -sS -sV --version-all -p- --open --defeat-rst-ratelimit -T3 --script=default,"vuln and safe",reverse-index --script-args http.useragent="Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko" --script-timeout 1020m --stats-every 240s --host-timeout 1240m --randomize-hosts -oA result_AllPorts_sS_sC_sV`
	* All TCP Ports, Service Enumeration, Default, Safe Scripts

* `nmap -iL targets.txt -Pn -sS -p- -T1 -open --max-hostgroup 5 --defeat-rst-ratelimit --script=reverse-index --stats-every 240s --host-timeout 1080m --randomize-hosts -oA TCP_AllPorts_sS_T1 `
	* All TCP ports, no scripts, slow (in order to validate what ports are open for comparison with more detailed scans, in order to detect any IPS)

* Nmap discovery scan of full TCP range (1-65535) can be automated using `monkiirobot.rb` tool, use the following command: 
 	* `sudo ruby monkiirobot.rb nmap-tcpfull `




### masscan

* `sudo masscan --rate=4000 -n -Pn --randomize-hosts -p8080 10.1.1.1 `
    * single target prep test
* `sudo nmap -Pn -n -p8080 10.1.1.1`
    * quick nmap to validate 

* `sudo masscan --rate=4000 -n -Pn --randomize-hosts -p1-65535 10.1.1.1 -oX massLas0.xml `

* `sudo masscan --rate=4000 -n -Pn --randomize-hosts -p1-65535 10.1.1.1/23 -oX massLas0.xml `

* `sudo masscan --rate=4000 -n -Pn --randomize-hosts -p1-65535 10.1.1.1/23 -oX massLas0.xml --source-ip 192.168.1.99 `
   * masscan contains its own TCP/IP stack separate from the system you run it on. If using masscan for banner grabbing, fake source IP from your local subnet may need to be provided as `--source-ip`. When the local system receives a SYN-ACK from the probed target, it responds with a RST packet that kills the connection before masscan can grab the banner. Consider only using masscan for port-scanning, and banner grab, service version with nmap - details tool readme https://github.com/robertdavidgraham/masscan#banner-checking


example to calculate estimate complation time of a scan
```
65535 possible ports x 510 hosts in a /23 (1/8th chunk of /20) 
33422850 total ports / 20k packets per sec scan rate
1671 sec = 28 minutes
```

**If using Atlanta scan infrastructure do not set a pps higher than 100, use the Softlayer sl-scan-1 and sl-scan-2 instead**


<br>
<br>

### Port-scan Results Parsing
Once scans complete, to parse results into CSV and individual files containing IPs with same open port (in format \<port-number\>.open, for example "445.open"), run the following command:
* `sudo ruby monkiirobot.rb parseonly`

<br> To parse, the tool requires that Nmap log files (in .xml and .gnmap) reside in directory `./monkiilog`.  Refer to help page for details - https://github.ibm.com/Piotr-Marszalik/monkiirobot#util-commands
<br> 


<br>
<br>
<br>
-----<br>
!!!!python parser script in below example has bugs, it may fail/crash when parsing. Use ruby tool monkiirobot.rb from above example. 
<br> 
//// <br> 
The following repo contains python v3 scripts which allow for parsing Nmap and Masscan XML results into human readable CSV format. CSV allows for fields of interest to be quickly sorted and filtered through excel or grep/cut/awk/sed-fu.

https://github.com/addenial/parse

Parse every nmap .xml in current directory into CSV, show ip,port,service info:

`python3 ./nmap-xml2csv-services.py -f '*' -csv services.csv `

Parse every .xml masscan result file in current directory, save combined output into file:

`python3 ./masscan_parse_full.py -f '*' -o outt.csv`

If you recieve an error that the XML is not formatted correctly, this may be due to the scan being interrupted prior completion. The script `fixXML.py` checks if each .xml file in directory ends in " \</nmaprun\> ". Appends it if not, to allow xml parsing of unfinished scans. 

To display only unique lines from CSV file
`python3 uniqMeCSV.py results.csv`

For details and additional examples, see Readme - https://github.com/addenial/parse/blob/main/README.md



additional examples:

Services - (TCP and UDP port scan results, versions)
`IP,port,proto,service,product,version,extra info,os type,hostname`

* `python ./nmap-xml2csv-services.py -f nmap-sv.xml -p `
	* parse and print to screen only
* `python ./nmap-xml2csv-services.py -f nmap-sv.xml -csv services.csv`
	* parse and save result to CSV


OS information -
`IP,OS family,vendor,osgen,type,os match name,accuracy`

* `python ./nmap-xml2csv-OSinfo.py -f nmap-output.xml -p `
	* parse and print to screen only
* `python ./nmap-xml2csv-OSinfo.py -f nmap-output.xml -csv parsed-OS-info.csv`
	* parse and save result to CSV


```
wget https://raw.githubusercontent.com/addenial/parse/main/nmap-xml2csv-services.py

python3 ./nmap-xml2csv-services.py -f TCP_Top2ksV.xml UDP_Top500sUsV.xml -p
python3 ./nmap-xml2csv-services.py -f TCP_Top2ksV.xml UDP_Top500sUsV.xml -csv targetslite-tcpudp.csv


find all uniq ports-
cat all_active_targets.csv | cut -d, -f2 | sort | uniq | sed -z "s/\n/,/g" 

```
### Nmap ICMP
Example of using Nmap to peform ping sweeps and detect active hosts and active subnets through ICMP. 

Hosts often have ICMP disabled. Having single instance of host ICMP response is typically indicative of entire /24 subnet being active. Other hosts within those potentially active subnets may be discovered by running more thorough port-scans. 


* `nmap -v -sn -n --reason -iL subnets.txt -oA nmap-pings`
	* ping sweep against range
* `screen -dmS icmps bash -c 'sudo nmap -iL ips.txt -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms -oA nmap-pings ' ` 
    *  ICMP scan in screen example


Example Nmap scripts for running ICMP pingsweep across RFC 1918 private range 192.168.x.x


```
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.0.0/20 -oX nmap-pings1.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.16.0/20 -oX nmap-pings2.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.32.0/20 -oX nmap-pings3.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.48.0/20 -oX nmap-pings4.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.64.0/20 -oX nmap-pings5.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.80.0/20 -oX nmap-pings6.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.96.0/20 -oX nmap-pings7.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.112.0/20 -oX nmap-pings8.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.128.0/20 -oX nmap-pings9.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.144.0/20 -oX nmap-pings10.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.160.0/20 -oX nmap-pings11.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.176.0/20 -oX nmap-pings12.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.192.0/20 -oX nmap-pings13.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.208.0/20 -oX nmap-pings14.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.224.0/20 -oX nmap-pings15.xml
nmap -v -n -sn -PE --reason -T4 --min-rtt-timeout 200ms --max-rtt-timeout 800ms --min-parallelism 20 --min-hostgroup 4096 --initial-rtt-timeout 800ms 192.168.240.0/20 -oX nmap-pings16.xml
```
	



Nmap result XML parsing examples - proof-of-concept - https://github.com/addenial/parse 

* `python ./nmap-xml2csv-icmp.py -f nmap-pings.xml -p`
	* parse and print to screen individual IPs of hosts that responded to ping

* `python ./nmap-xml2csv-icmp.py -f nmap-pings.xml -csv pingz.csv`
	* parse and save result to CSV


Use to parse hosts that responded to ICMP, round to nearest /24, and show uniques subnets

* `python ./nmap-xml2csv-icmp.py -f nmap-pings.xml -subs`
	* parse and find active /24 subnets

* `python ./nmap-xml2csv-icmp.py -f nmap-pings.xml -subs -csv active-subnets.csv`
	* parse and find active subnets, save to csv

example to parse 192.168.x.x ICMP pingsweep - 
show all hosts that responded to ICMP, derive /24 subnets, for every .xml in current working directory::

```
python3 ./nmap-xml2csv-icmp.py -f '*' -subs -csv active-subnets.csv 
```


 occasionally may need additional `cat active-subnets.csv | sort | uniq` if non-standard subnet breakouts 

### Nmap SMB
* Example of using nmap for an unauthenticated scan to check status of SMB Message Signing setting on hosts.

Single target check:
```
nmap --script smb-security-mode -Pn -n -sS -p 445 <IP>
```

Using input file of targets and saving results in all formats (.xml, .gnmap, .nmap):
```
nmap --script smb-security-mode -Pn -n -sS -p 445 -iL <ip-ranges-file> -oA <results-smb-signing>
```

### Nmap MSSQL
* Example of using nmap to enumerate MSSQL database instances across Windows hosts.

The ms-sql-info recon nse script does not require credentials and when used against a Windows host, it will attempt to determine if Microsoft SQL is installed, query for the available databases, SQL instance information, and associated instance TCP ports and named pipes.


Single target check:
```
nmap -Pn -n -p135,445,1433 --script ms-sql-info <host> -oX results-ms-sql-info.xml
```

Using hosts file and saving results into .xml format:
```
nmap -Pn -n -p135,445,1433 --script ms-sql-info -iL <hosts_file> -oX results-ms-sql-info.xml
```


To find useful information, ms-sql-info XML output can be parsed into CSV file using the following script - https://github.com/addenial/mssqlinfo2csv

`python ./mssql-info-parser.py results-ms-sql-info.xml > parsed-mssql.csv`

The script pulls and parses the following fields of interest-

`IP,TCPport,Winservername,Instance,ProductVersionName,Named Pipe`

Fields details~ IP Address, Instance TCP Port, Windows Server Name, SQL Server Instance, SQL Version Product Name Number Service Pack, Instance Named Pipe

## Nessus Vulnerability Scanning 
In cases where running Nessus on an internal test is required or requested by the client, you may need to install Nessus on the RPT. Refer to the reference #1 installing and running Nessus on the RPT.

If the project is preapproved to use a Nessus license, refer to the #2 reference. 

1. [Installing Nessus on RPT](https://ibm.ent.box.com/notes/440130058455?s=6ydlpeejg6f7y1xrmjv5o1wj4056xgyb)
2. [Requesting Nessus License](https://ibm.ent.box.com/notes/425024916381)

## [[https://github.ibm.com/X-Force-Red/Testing-Methodology/blob/master/icons/icons8-book-shelf-50.png]] Further Reading
* https://nmap.org/ 
* https://nmap.org/book/man.html
* https://nmap.org/nsedoc/scripts/smb-security-mode.html
* https://nmap.org/nsedoc/scripts/ms-sql-info.html



## PowerShell port-scanning

examples one-liners

```
cmd.exe

powershell "function opentcp{$ports=(445);$ip="""127.0.0.1""";foreach ($port in $ports) {try{$socket=New-object System.Net.Sockets.TCPClient ($ip,$port);}catch{};if ($socket -eq $NULL){}else{echo $ip""":"""$port""" - Open""";$socket = $NULL;}} }opentcp "





function opentcp{$ports=(445);$ip="127.0.0.1";foreach ($port in $ports) {try{$socket=New-object System.Net.Sockets.TCPClient ($ip,$port);}catch{};if ($socket -eq $NULL){}else{echo $ip":"$port" - Open";$socket = $NULL;}} }opentcp


function opentcp{$ports=(22);$ip="10.40.131.238";foreach ($port in $ports) {try{$socket=New-object System.Net.Sockets.TCPClient ($ip,$port);}catch{};if ($socket -eq $NULL){}else{echo $ip":"$port" - Open";$socket = $NULL;}} }opentcp


function opentcp{$ports=(21,22,23,80,88,135,389,443,445,3389,5985,5986,5900,5901,8080,8443);$ip="IPADDRESSHEREEE";foreach ($port in $ports) {try{$socket=New-object System.Net.Sockets.TCPClient ($ip,$port);}catch{};if ($socket -eq $NULL){}else{echo $ip":"$port" - Open";$socket = $NULL;}} }opentcp



| out-file out_tcp.txt



```
One-liner- multiple IPs and multiple ports from arrays. 
```
function opentcp{ 
$ips=( "127.0.0.1","127.0.2.2","127.0.3.3","127.0.4.4" ) ; $ports=(22,389,636,443,445,3389,5985,5986);  
foreach ($ip in $ips) { foreach ($port in $ports) { try{$socket=New-object System.Net.Sockets.TCPClient ($ip,$port);}catch{};if ($socket -eq $NULL){}else{echo $ip":"$port" - Open";$socket = $NULL;}}  } }opentcp 
```


Invoke-PortScan and other examples-

```
Import-Module .\port-scan-tcp.ps1 -force
Import-Module .\port-scan-udp.ps1 -force

#single host
port-scan-tcp 10.16.40.233 (21,22,23,80,88,135,389,443,445,3389,5985,5986,5900,5901,8080,8443)

#scan range 
0..255 | foreach { port-scan-tcp 10.16.40.$_ (22,80,445) }

#file 
port-scan-tcp (gc .\computers.txt) 445

#result 
Get-Content .\scanresults.txt | Select-String "tcp,445,Open"


https://github.com/InfosecMatter/Minimalistic-offensive-security-tools/blob/master/port-scan-tcp.ps1
https://github.com/InfosecMatter/Minimalistic-offensive-security-tools/blob/master/port-scan-udp.ps1
```

Other techniques to check open ports with less characters:

```
#on kali
python -m http.server 80
python -m http.server 8888

#client
powershell curl http://10.40.131.238
powershell curl http://10.40.131.238:8888

cmd
powershell "$tcp = New-Object Net.Sockets.TcpClient; $tcp.Connect("""10.40.131.238""", 8888); if ($tcp.Connected) { echo """open 8888""" }; $tcp.Close()"

powershell
$tcp = New-Object Net.Sockets.TcpClient; $tcp.Connect("10.40.131.238", 8888); if ($tcp.Connected) { echo "open 8888" }; $tcp.Close()

```


## [[https://github.ibm.com/X-Force-Red/Testing-Methodology/blob/master/icons/icons8-ninja-filled-50.png]] SMEs

Please reach out to these folks if you need help:

Name | Email | Notes
| --- | --- | --- |
| _Piotr Marszalik_  | _piotr.marszalik@ibm.com_ | |


