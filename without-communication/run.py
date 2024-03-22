from model import MoneyModel
import seaborn as sns

model = MoneyModel(50, 10, 10)  # 50 agents in our example
for i in range(100):
    model.step()

gini = model.datacollector.get_model_vars_dataframe()["Gini"]

g = sns.lineplot(data=gini)
g.set(title="Gini Coefficient over Time", ylabel="Gini Coefficient")
