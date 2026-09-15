import gradio as gr
import pandas as pd

import plotly.graph_objects as go

class LeaderBoard:
    def __init__(self, df):
        self.df =df

    def build_leaderboard_tab(self):
    
        # Stwórz tabelę w Gradio
        leaderboard_df_styled = self.df.style.background_gradient(cmap="RdYlGn")
        rounding = {}
        for col in self.df.columns.tolist():
            if col=='Model': continue
            rounding[col] = "{:.2f}"
        leaderboard_df_styled = leaderboard_df_styled.format(rounding)
        leaderboard_table = gr.Dataframe(value=leaderboard_df_styled,
                                        interactive=False, 
                                        wrap = False,
                                        headers=self.df.columns.tolist(),
                                        col_count=len(self.df.columns.tolist())
                                        )
        
        return (leaderboard_table,)



    def build_leaderboard_checkboxes(self):
        
        top3_models = self.df["Model"].tolist()[6]
        return gr.CheckboxGroup(self.df['Model'].tolist(), label="Modele", value=top3_models)
    
    def build_leaderboard_plot(self, model_names):


        # Melt the dataframe to long format
        dfx = self.df.copy()
        dfx = dfx.drop(columns=['pl_wynik', 'odpowiedzi_pl'])
        #df = self.df.melt(id_vars=["Model"], var_name="Task", value_name="Score").sort_values(by="Task")
        df = dfx.melt(id_vars=["Model"], var_name="Task", value_name="Score").sort_values(by="Task")

        # df.drop(columns=['pl_wynik', 'odpowiedzi_pl'])

        # Populate figure
        fig = go.Figure()
        for model_name in model_names:
            model_df = df[df["Model"] == model_name]
            scores = model_df["Score"].tolist()
            tasks = model_df["Task"].tolist()

            # Repeat the first point at the end to close the lines
            # Cf. https://community.plotly.com/t/closing-line-for-radar-cart-and-popup-window-on-chart-radar/47711/4
            scores.append(scores[0])
            tasks.append(tasks[0])

            fig.add_trace(go.Scatterpolar(r=scores, theta=tasks, name=model_name))

        fig.update_layout(
            title="Wyniki modeli na poszczególnych zadaniach",
        )

        

        return fig

