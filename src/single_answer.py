import gradio as gr
import pandas as pd
import re

from common import get_single_judge_explanation, post_process_answer, resolve_single_judgment_dict, sort_models



class SingleAnswer:
    def __init__(self, question_selector_map, category_selector_map, model_answers, model_judgments_normal_single, model_judgments_math_single):
        self.question_selector_map = question_selector_map
        self.category_selector_map = category_selector_map
        self.model_answers = model_answers
        self.model_judgments_normal_single = model_judgments_normal_single
        self.model_judgments_math_single = model_judgments_math_single


    def display_question(self, category_selector):
        choices = self.category_selector_map[category_selector]
        return gr.Dropdown(
            value=choices[0],
            choices=choices,
        )




    def single_to_gradio_chat_mds(self, question, ans, turn=None):
        end = len(question["turns"]) if turn is None else turn + 1

        mds = ["", "", "", "", ""]
        for i in range(end):
            base = i * 2
            if i == 0:
                mds[base + 0] = "##### Użytkownik\n" + question["turns"][i]
            else:
                mds[base + 0] = "##### Pytanie uzupełniające użytkownika \n" + question["turns"][i]
            mds[base + 1] = "##### Asystent A\n" + post_process_answer(
                ans["choices"][0]["turns"][i].strip()
            )

        ref = question.get("reference", ["", ""])

        ref_md = ""
        if turn is None:
            if ref[0] != "" or ref[1] != "":
                mds[4] = f"##### Rozwiązanie referencyjne\nQ1. {ref[0]}\nQ2. {ref[1]}"
        else:
            x = ref[turn] if turn < len(ref) else ""
            if x:
                mds[4] = f"##### Rozwiązanie referencyjne\n{ref[turn]}"
            else:
                mds[4] = ""
        return mds


    def display_single_answer(self, question_selector, model_selector1):
        q = self.question_selector_map[question_selector]
        qid = q["question_id"]

        ans1 = self.model_answers[model_selector1][qid]

        chat_mds = self.single_to_gradio_chat_mds(q, ans1)
        gamekey = (qid, model_selector1)

        judgment_dict = resolve_single_judgment_dict(
            q, self.model_judgments_normal_single, self.model_judgments_math_single, multi_turn=False
        )

        explanation = "##### Ocena modelu (pierwsza tura)\n" + get_single_judge_explanation(
            gamekey, judgment_dict
        )

        judgment_dict_turn2 = resolve_single_judgment_dict(
            q, self.model_judgments_normal_single, self.model_judgments_math_single, multi_turn=True
        )

        explanation_turn2 = (
            "##### Ocena modelu (druga tura)\n"
            + get_single_judge_explanation(gamekey, judgment_dict_turn2)
        )

        return chat_mds + [explanation] + [explanation_turn2]


   

  




    def build_single_answer_browser_tab(self):

        models = sort_models(list(self.model_answers.keys()))
        num_sides = 1
        num_turns = 2
        side_names = ["A"]

        question_selector_choices = list(self.question_selector_map.keys())
        category_selector_choices = list(self.category_selector_map.keys())

        # Selectors
        with gr.Row():
            with gr.Column(scale=1, min_width=200):
                category_selector = gr.Dropdown(
                    choices=category_selector_choices, label="Kategoria", container=False
                )
            with gr.Column(scale=100):
                question_selector = gr.Dropdown(
                    choices=question_selector_choices, label="Pytanie", container=False
                )

        model_selectors = [None] * num_sides
        with gr.Row():
            for i in range(num_sides):
                with gr.Column():
                    model_selectors[i] = gr.Dropdown(
                        choices=models,
                        value=models[i] if len(models) > i else "",
                        label=f"Model {side_names[i]}",
                        container=False,
                    )

        # Conversation
        chat_mds = []
        for i in range(num_turns):
            chat_mds.append(gr.Markdown(elem_id=f"user_question_{i+1}"))
            with gr.Row():
                for j in range(num_sides):
                    with gr.Column(scale=100):
                        chat_mds.append(gr.Markdown())

                    if j == 0:
                        with gr.Column(scale=1, min_width=8):
                            gr.Markdown()

        reference = gr.Markdown(elem_id=f"reference")
        chat_mds.append(reference)

        model_explanation = gr.Markdown(elem_id="model_explanation")
        model_explanation2 = gr.Markdown(elem_id="model_explanation")

        # Callbacks
        category_selector.change(self.display_question, [category_selector], [question_selector])
        question_selector.change(
            self.display_single_answer,
            [question_selector] + model_selectors,
            chat_mds + [model_explanation] + [model_explanation2],
        )

        for i in range(num_sides):
            model_selectors[i].change(
                self.display_single_answer,
                [question_selector] + model_selectors,
                chat_mds + [model_explanation] + [model_explanation2],
            )

        return (category_selector,)

