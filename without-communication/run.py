import mesa
import pandas as pd
import matplotlib.pyplot as plt

from model import NuclearWasteModel

params = {  # These are the parameters that will be passed to the model
    "width": 60,
    "height": 50,
    "n_green_agents": 5,
    "n_yellow_agents": 5,
    "n_red_agents": 5,
    "n_wastes": 50,
    "max_wastes_handed": 2,
    "strategy": 3,
}

# params = {  # These are the parameters that will be passed to the model
#     "width": 12,
#     "height": 10,
#     "n_green_agents": 1,
#     "n_yellow_agents": 1,
#     "n_red_agents": 1,
#     "n_wastes": 10,
#     "max_wastes_handed": 2,
#     "strategy": 3,
# }

results = mesa.batch_run(
    NuclearWasteModel,
    parameters=params,
    iterations=10,
    max_steps=1500,
    number_processes=1,
    data_collection_period=1,
    display_progress=True,
)
results_df = pd.DataFrame(results)
results_df = results_df[results_df["Type"] != "RadioactivityAgent"]
results_df = results_df[results_df["Type"] != "WasteAgent"]


save_path = "without-communication/results.csv"
results_df.to_csv(save_path)
print(f"Results saved at {save_path}")


df = results_df
grouped = df.groupby("Step")["accessible_remaining_wastes"].agg(["mean", "std"])
plt.figure(figsize=(10, 6))

for run_id in df["RunId"].unique():
    subset = df[df["RunId"] == run_id]
    plt.plot(
        subset["Step"],
        subset["accessible_remaining_wastes"],
        # label=f"Run {run_id} Remaining Waste",
    )

nb_runs = len(df[df["accessible_remaining_wastes"] == 0]["RunId"].unique())
print(f"Number of runs that reached the end: {nb_runs}/{df['RunId'].nunique()}")

plt.plot(
    grouped.index,
    grouped["mean"],
    label="Average Remaining Waste",
    color="black",
    linestyle="--",
)
plt.title(
    "Strategy 3 : Evolution of Remaining Waste over Steps on grid 60x50 (Pattern Improved)"
)
plt.xlabel("Step")
plt.ylabel("Waste Remaining")
plt.legend()
plt.grid(True)


# Adding text annotation for parameters
params_text = "\n".join(f"{key}: {value}" for key, value in params.items())
params_text = f"Parameters:\n{params_text}"
plt.annotate(
    params_text,
    xy=(0.7, 0.68),
    xycoords="axes fraction",
    fontsize=8,
    bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="whitesmoke"),
)

# Add a comment about the number of runs that reached the end
plt.annotate(
    f"Number of finished runs: {nb_runs}/{df['RunId'].nunique()}",
    xy=(0.7, 0.6),
    xycoords="axes fraction",
    fontsize=8,
    bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="whitesmoke"),
)

plt.show()
