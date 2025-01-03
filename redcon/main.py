from agent import Agent

if __name__ == "__main__":
    agent = Agent()
    # agent.run()
    context = agent.rag_query({"query":"what is the nmpa command to find all domain controllers on the network"})
    for c in context:
        print(c)
        print("")
    print("")
    print("="*50)
    print("")
    context = agent.rag_query({"query":"how do i determine if ldap signing is enabled?"})
    for c in context:
        print(c)
        print("")