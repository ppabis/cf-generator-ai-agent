import ell

class Configuration:
    def __init__(self, commit_model: str = "gpt-4o-mini", agent_model: str = "gpt-4o-mini", client = None):
        self.commit_model = commit_model
        self.agent_model = agent_model
        self.client = client
        ell.init(store="log", autocommit=True, autocommit_model=self.commit_model, default_client=self.client)

