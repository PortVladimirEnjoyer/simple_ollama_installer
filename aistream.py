
"""
this is the conversation ui script , its what 
allow the users to talk with their model of choice 



"""



import subprocess
import time
import tkinter as tk
from tkinter import scrolledtext
import requests
import threading




#first a function to launch the model 

def start_model(model):
    try:
        process = subprocess.Popen(
            ["ollama", "run", model],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"[Info] Launched model '{model}', waiting for it to load...")
        time.sleep(5)  # Allow time for the model to load
        print(f"[Info] Model '{model}' should now be ready.")
        return process
    except FileNotFoundError:
        print("[Error] Ollama not found. Make sure it's installed and in your PATH.")
    except Exception as e:
        print(f"[Error launching model] {e}")

def send_to_ollama(message, model_name):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": message}],
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['message']['content']
    except Exception as e:
        return f"[Error] {e}"





class OllamaChatGUI:
    def __init__(self, root, model_name):
        self.root = root
        self.model_name = model_name  # Store model name 
        self.root.title("Ollama Chat")

        # Conversation display
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", height=25)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # User input frame
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        self.user_input = tk.Text(self.input_frame, height=3)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.handle_enter)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(10,0))

    def handle_enter(self, event):
        if not event.shift:
            self.send_message()
            return "break"

    def send_message(self):
        user_text = self.user_input.get("1.0", tk.END).strip()
        if not user_text:
            return

        self.append_chat("You", user_text)
        self.user_input.delete("1.0", tk.END)

        threading.Thread(target=self.get_response, args=(user_text,), daemon=True).start()

    def get_response(self, message):
        response = send_to_ollama(message, self.model_name)
        self.append_chat(self.model_name.capitalize(), response)

    def append_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, f"{sender}:\n{message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)












if __name__ == "__main__":
    root = tk.Tk()
    app = OllamaChatGUI(root)
    root.geometry("600x700")
    root.mainloop()

