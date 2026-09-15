import argparse
from collections import defaultdict
import base64
import gradio as gr



from content import *

from src.leaderboard import *
from src.about import *
from src.pairwise_browser import *
from src.single_answer import *

from common import (
    get_mt_bench_results,
    load_questions,
    load_model_answers,
    load_single_model_judgments,
    load_pairwise_model_judgments,
)




questions = []
model_answers = {}

model_judgments_normal_single = {}
model_judgments_math_single = {}

model_judgments_normal_pairwise = {}
model_judgments_math_pairwise = {}

question_selector_map = {}
category_selector_map = defaultdict(list)

# wyniki benchmarku
result_df = None



def build_question_selector_map():
    global question_selector_map, category_selector_map

    # Build question selector map
    for q in questions:
        preview = f"{q['question_id']}: " + q["turns"][0][:128] + "..."
        question_selector_map[preview] = q
        category_selector_map[q["category"]].append(preview)




block_css = """
#user_question_1 {
    background-color: #b77522;
    color: black !important;}
#user_question_2 {
    background-color: #2c9eb1d4;
    color: black !important;}
#reference {
    background-color: #8e45a8d4;
    color: black !important;
}
#model_explanation {
    background-color: #859172d4;
    color: black !important;
}
"""


def load_demo():
    dropdown_update = gr.Dropdown(value=list(category_selector_map.keys())[1])
    return dropdown_update, dropdown_update

def encode_image_to_base64(filepath):
    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

encoded_image = encode_image_to_base64('assets/pl_small.png')
image_markdown = f'![](data:image/png;base64,{encoded_image})'

def build_demo():
    build_question_selector_map()

    with gr.Blocks(
        title="Przeglądarka polskiego MT-Bench",
        theme=gr.themes.Base(text_size=gr.themes.sizes.text_lg),
        css=block_css,
    ) as demo:
        gr.Markdown(
#             """
# # Polski MT-Bench {image_markdown}
# | [Publikacja](https://arxiv.org/abs/2306.05685) | [Kod](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge) | [Chatbot Arena Leaderboard](https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard) |
# """ 
            f"""
# Polski MT-Bench {image_markdown}
| [Publikacja](https://arxiv.org/abs/2306.05685) | [Kod](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge) | [Chatbot Arena Leaderboard](https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard) |
"""
        )
        with gr.Tab("Tablica wyników"):
            leader_board = LeaderBoard(result_df)

            (category_selector3,) = leader_board.build_leaderboard_tab()
            gr.Markdown("**pl_wynik** - końcowy wynik po uwzględnieniu % odpowiedzi udzielonych w języku polskim.<br> **odpowiedzi_pl** - % odpowiedzi w języku polskim (modele częściowo odpowiadają językiem angielskim mimo zadania w języku polskim).<br> **średni wynik** - oznacza ocenę GPT bez względu na język odpowiedzi. ")
            gr.Markdown("## Wizualizacja")
            with gr.Row():
                with gr.Column():
                    buttons = leader_board.build_leaderboard_checkboxes()
        
                with gr.Column(scale=2):
                    plot = gr.Plot(container=True)
                    buttons.change(leader_board.build_leaderboard_plot, inputs=buttons, outputs=[plot])
                    demo.load(leader_board.build_leaderboard_plot, inputs=buttons, outputs=[plot])


        with gr.Tab("Ocena pojedynczego pytania"):
            single_answer = SingleAnswer(question_selector_map, category_selector_map, model_answers, model_judgments_normal_single, model_judgments_math_single)
            (category_selector,) = single_answer.build_single_answer_browser_tab()

        with gr.Tab("Porównanie parami"):
            pairwise_browser = PairwiseBrowser(question_selector_map, category_selector_map, model_answers, model_judgments_normal_pairwise, model_judgments_math_pairwise)
            (category_selector2,) = pairwise_browser.build_pairwise_browser_tab()

        with gr.Tab("Opis"):
            (category_selector4,) = build_about_tab()
            gr.Markdown(CREDIT, elem_classes="markdown-text")

      
        demo.load(load_demo, [], [category_selector, category_selector2])
        # demo.load(load_demo, [], [category_selector])
    
    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int)
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--bench-name", type=str, default="mt_bench")
    args = parser.parse_args()
    print(args)

    result_file = f"data/{args.bench_name}/mt-bench.csv"


    question_file = f"data/{args.bench_name}/question.jsonl"
    answer_dir = f"data/{args.bench_name}/model_answer"

    pairwise_model_judgment_file = (f"data/{args.bench_name}/model_judgment/gpt-4_pair.jsonl")
    single_model_judgment_file = (f"data/{args.bench_name}/model_judgment/gpt-4_single.jsonl")

    # Load questions
    questions = load_questions(question_file, None, None)

    # Load answers
    model_answers = load_model_answers(answer_dir)

    # Load model judgments
    model_judgments_normal_single = (
        model_judgments_math_single
    ) = load_single_model_judgments(single_model_judgment_file)

    model_judgments_normal_pairwise = (
        model_judgments_math_pairwise
    ) = load_pairwise_model_judgments(pairwise_model_judgment_file)


    result_df = get_mt_bench_results(result_file)

    demo = build_demo()
    demo.launch(
        server_name=args.host, server_port=args.port, share=args.share, max_threads=200, debug=True
    )