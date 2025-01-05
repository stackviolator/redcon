from agent import Agent

if __name__ == "__main__":
    # model = "llama3.1:8b" # damn this thing is stupid
    model = "gpt-4o"
    agent = Agent(model=model)
    # agent.run_nmap_scan({"args":"-p 88,135-139,445 -sVC -oA scans/nmap/domainControllers","outfile":"scans/nmap/domainControllers.xml","target":"172.16.29.0/24"})
    agent.run()