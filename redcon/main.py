from redcon.agents.ReasoningAgent import ReasoningAgent

if __name__ == "__main__":
    # model = "llama3.1:8b" # damn this thing is stupid
    model = "gpt-4o"
    agent = ReasoningAgent(model=model)
    # agent.run_nmap_scan({"args":"ballsack lol"})
    print(agent.rag_query({"query":"Domain controller recon techniques"}))
    # agent.run()