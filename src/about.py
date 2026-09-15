import gradio as gr
import pandas as pd

def build_about_tab():
    html_content = """
        <p>
        <div align="center"><img src="https://speakleash.org/wp-content/uploads/2023/09/SpeakLeash_logo.svg"/></div>
        </p>
        <br/>
        <div align="center"><h1>Polski MT-Bench</h1></div>
        <p>
        MT-bench jest narzędziem przeznaczonym do testowania zdolności modeli językowych (LLM) do prowadzenia wieloetapowych konwersacji i wykonywania instrukcji. Obejmuje typowe przypadki użycia i koncentruje się na trudnych pytaniach, aby odróżnić możliwości różnych modeli. Zidentyfikowano 8 głównych kategorii zapytań użytkownika, które posłużyły do skonstruowania MT-bench:</br>
         <ul>
          <li>pisanie</li>
          <li>odgrywanie ról</li>
          <li>ekstrakcja informacji</li>
          <li>rozumowanie</li>
          <li>matematyka</li>
          <li>kodowanie</li>
          <li>wiedza / nauki ścisłe</li>
          <li>wiedza / nauki humanistyczne/społeczne)</li>
          </ul>
          <br/>
          Dla każdej kategorii opracowano ręcznie wieloetape pytania. Przykład poniej:
        </p>
        <br/>
        <p>
          Tura 1: Rozważmy satelitę na kołowej orbicie wokół Ziemi. Prędkość satelity maleje. Co stanie się z promieniem orbity i okresem obrotu satelity? Uzasadnij swoją odpowiedź, odwołując się do zasad fizyki.
        </p>
        <p>
          Tura 2: Jakie przypadki szczególne uwzględniasz? Jak sobie z nimi poradzisz?
        </p>
        <p>
        Ocenę odpowiedzi wykonuje metamodel. W przypadku MT-Bench jest to model GPT-4. Dzięki zastosowaniu metamodelu możemy weryfikować odpowiedzi pochodzące z pytań otwartych np. napisz artykuł dotyczący samochodów hybrydowych. Model ocenia treść wypowiedzi, jakość użytych faktów, kreatywność itd.
        </p>
        <p>
        Polski MT-Bench został całkowicie spolonizowany. Każde zadanie zostało najpierw maszynowo przetłumaczone po czym zweryfikowane. Dodatkowo wprowadziliśmy polskie akcenty np. zamiast opisu wakacji na Hawajach zaproponowaliśmy lokalizację - Mazury. W naszej wersji językowej zostało wprowadzone dużo zmian, które mają przenieść test w polskie realia językowe.
        </p>
     
    """
    # Utworzenie komponentu HTML z podaną zawartością
    about_tab = gr.HTML(value=html_content)

    # Zwrócenie komponentu do wykorzystania w zakładce
    return (about_tab,)
    