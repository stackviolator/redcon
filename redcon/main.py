from redcon.agents.ReasoningAgent import ReasoningAgent
from redcon.agents.SummaryAgent import SummaryAgent

if __name__ == "__main__":
    gpt = "gpt-4o"
    llama = "llama3.1:8b"

    agent = ReasoningAgent(model=gpt)
    agent.run()
    # sagent = SummaryAgent(model=llama)
    # sagent.run()


    # print(agent.rag_query({"query":"Domain controller recon techniques"}))
    # agent.run_nmap_scan({"args":"ballsack lol"})