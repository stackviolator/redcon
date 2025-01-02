from agent import Agent

if __name__ == "__main__":
    agent = Agent()
    print(agent.rag_query({"query":"What is the nmap command to find all windows workstations"}))
#    agent.run()