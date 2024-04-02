from model import NuclearWasteModel
import seaborn as sns

model = NuclearWasteModel(N_AGENTS=5, N_WASTES=10, width=100, height=100)
for i in range(10):
    model.step()
