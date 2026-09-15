import gradio as gr
import pandas as pd

from common import (
    get_mt_bench_results,
    load_questions,
    load_model_answers,
    load_single_model_judgments,
    load_pairwise_model_judgments,
    post_process_answer,
    resolve_single_judgment_dict,
    resolve_pairwise_judgment_dict,
    get_single_judge_explanation,
    get_pairwise_judge_explanation,
    sort_models,
)


class PairwiseBrowser:
    def __init__(self, question_selector_map, category_selector_map, model_answers, model_judgments_normal_pairwise, model_judgments_math_pairwise):
        self.question_selector_map = question_selector_map
        self.category_selector_map = category_selector_map
        self.model_answers = model_answers
        self.model_judgments_normal_pairwise = model_judgments_normal_pairwise
        self.model_judgments_math_pairwise= model_judgments_math_pairwise


    def display_question(self, category_selector):
        choices = self.category_selector_map[category_selector]
        return gr.Dropdown(
            value=choices[0],
            choices=choices,
        )


    def build_pairwise_browser_tab(self):
        global question_selector_map, category_selector_map

        models = sort_models(list(self.model_answers.keys()))
        num_sides = 2
        num_turns = 2
        side_names = ["A", "B"]

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
                    if i == 0:
                        value = models[0]
                    else:
                        value = "gpt-3.5-turbo"
                    model_selectors[i] = gr.Dropdown(
                        choices=models,
                        value=value,
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
            self.display_pairwise_answer,
            [question_selector] + model_selectors,
            chat_mds + [model_explanation] + [model_explanation2],
        )

        for i in range(num_sides):
            model_selectors[i].change(
                self.display_pairwise_answer,
                [question_selector] + model_selectors,
                chat_mds + [model_explanation] + [model_explanation2],
            )

        return (category_selector,)

    def pairwise_to_gradio_chat_mds(self, question, ans_a, ans_b, turn=None):
        end = len(question["turns"]) if turn is None else turn + 1

        mds = ["", "", "", "", "", "", ""]
        for i in range(end):
            base = i * 3
            if i == 0:
                mds[base + 0] = "##### Użytkownik\n" + question["turns"][i]
            else:
                mds[base + 0] = "##### Pytanie uzupełniające użytkownika \n" + question["turns"][i]
            mds[base + 1] = "##### Asystent A\n" + post_process_answer(
                ans_a["choices"][0]["turns"][i].strip()
            )
            mds[base + 2] = "##### Asystent B\n" + post_process_answer(
                ans_b["choices"][0]["turns"][i].strip()
            )

        ref = question.get("reference", ["", ""])

        ref_md = ""
        if turn is None:
            if ref[0] != "" or ref[1] != "":
                mds[6] = f"##### Rozwiązanie referencyjne\nQ1. {ref[0]}\nQ2. {ref[1]}"
        else:
            x = ref[turn] if turn < len(ref) else ""
            if x:
                mds[6] = f"##### Rozwiązanie referencyjne\n{ref[turn]}"
            else:
                mds[6] = ""
        return mds


    def display_pairwise_answer(
        self, question_selector, model_selector1, model_selector2
    ):
        q = self.question_selector_map[question_selector]
        qid = q["question_id"]

        ans1 = self.model_answers[model_selector1][qid]
        ans2 = self.model_answers[model_selector2][qid]

        chat_mds = self.pairwise_to_gradio_chat_mds(q, ans1, ans2)
        gamekey = (qid, model_selector1, model_selector2)

        judgment_dict = resolve_pairwise_judgment_dict(
            q,
            self.model_judgments_normal_pairwise,
            self.model_judgments_math_pairwise,
            multi_turn=False,
        )

        explanation = (
            "##### Ocena modelu (pierwsza tura)\n"
            + get_pairwise_judge_explanation(gamekey, judgment_dict)
        )

        judgment_dict_turn2 = resolve_pairwise_judgment_dict(
            q,
            self.model_judgments_normal_pairwise,
            self.model_judgments_math_pairwise,
            multi_turn=True,
        )

        explanation_turn2 = (
            "##### Ocena modelu (druga tura)\n"
            + get_pairwise_judge_explanation(gamekey, judgment_dict_turn2)
        )

        return chat_mds + [explanation] + [explanation_turn2]