from model import NuclearWasteModel

model = NuclearWasteModel(
    width=10,
    height=10,
    n_green_agents=10,
    n_yellow_agents=10,
    n_red_agents=10,
    n_wastes=10,
    max_wastes_handed=5,
    strategy=1,
)
for i in range(10):
    model.step()
