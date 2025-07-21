

"""

main script , this can detect if ollama is there or not , or if a given model 
name is there or not and after that install the given model or ollama
it runs the basic gui , the main window for model submission(not the window to talk with ai)


"""


import subprocess
import customtkinter as ctk
from tkinter import messagebox
from aistream import start_model, OllamaChatGUI

#GUI  
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Ollama Model Checker")
app.geometry("500x500")


title_label = ctk.CTkLabel(app, text="Ollama Model Checker", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=20)

model_entry = ctk.CTkEntry(app, placeholder_text="Enter model name (e.g. llama2)")
model_entry.pack(pady=10)

result_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=14), wraplength=400, justify="center")
result_label.pack(pady=20)


install_ollama_entry = None
install_ollama_button = None
install_model_entry = None
install_model_button = None
wanna_run_entry = None
wanna_run_button = None

#main functions
def install_ollama(): #installing ollama if its not there 
    try:
        subprocess.run("curl -fsSL --http1.1 https://ollama.com/install.sh | sh", shell=True, check=True)
        result_label.configure(text="Ollama installed successfully. You can now check your model.", text_color="green")
        install_ollama_entry.pack_forget()
        install_ollama_button.pack_forget()
        return True
    except subprocess.CalledProcessError as error:
        messagebox.showwarning("Subprocess Error", "Check your terminal.")
        print(error)
        return False

def handle_ollama_decision(choice):  #decision handler if user decides to install ollama
    choice = choice.strip().upper()
    if choice == "Y":
        install_ollama()
    elif choice == "N":
        result_label.configure(text="Ollama installation canceled.", text_color="orange")
        install_ollama_entry.pack_forget()
        install_ollama_button.pack_forget()
    else:
        result_label.configure(text="Invalid input. Please type Y or N.", text_color="orange")

def is_ollama_installed():
    try:
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_model_installed(model_name): #checking if ollama is installed 
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        model_name = model_name.lower()

        installed_models = []
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 1:
                installed_models.append(parts[0].lower())  # e.g. "llama2:latest"

        for m in installed_models:
            if m.startswith(model_name + ":") or m == model_name:
                return True

        return False
    except Exception as e:
        print("Model check error:", e)
        return False

def install_model(model_name):  #function for installing a desired model 
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        result_label.configure(text=f"Model '{model_name}' pulled successfully!", text_color="green")
        install_model_entry.pack_forget()
        install_model_button.pack_forget()
    except subprocess.CalledProcessError:
        result_label.configure(text=f"Failed to pull model '{model_name}'.", text_color="red")

def handle_model_decision(choice, model_name):#here is the function for handeling the decision of the desired model 
    choice = choice.strip().upper()
    if choice == "Y":
        install_model(model_name)
    elif choice == "N":
        result_label.configure(text="Model installation skipped.", text_color="orange")
        install_model_entry.pack_forget()
        install_model_button.pack_forget()
    else:
        result_label.configure(text="Invalid input. Please type Y or N.", text_color="orange")

def handle_run_decision(model_name): #this is the handler for the running decision so if the useeer wants to launch it or not
    decision = wanna_run_entry.get().strip().lower()
    if decision == "y":
        start_model(model_name) #this function is from the script aistream.py
        root = ctk.CTk()
        OllamaChatGUI(root, model_name) #this is the main class of aistream.py 
        root.mainloop()

        wanna_run_entry.pack_forget()
        wanna_run_button.pack_forget()
    elif decision == "n":
        result_label.configure(text="alrg gng", text_color="orange")
        wanna_run_entry.pack_forget()
        wanna_run_button.pack_forget()
    else:
        result_label.configure(text="Invalid input. Please type Y or N.", text_color="orange")

def check_model(): #main function ; its for checking if the model is there and if the user wants to install ollama and the model (if not there)
    global install_ollama_entry, install_ollama_button
    global install_model_entry, install_model_button
    global wanna_run_entry, wanna_run_button

    model_name = model_entry.get().strip().lower()
    if not model_name:
        messagebox.showwarning("Input Error", "Please enter a model name.")
        return

    if not is_ollama_installed():
        result_label.configure(text="Ollama is not installed. Would you like to install it? (Y/N)", text_color="red")
        install_ollama_entry = ctk.CTkEntry(app, placeholder_text="Type Y to install Ollama")
        install_ollama_entry.pack(pady=5)
        install_ollama_button = ctk.CTkButton(app, text="Submit", command=lambda: handle_ollama_decision(install_ollama_entry.get()))
        install_ollama_button.pack(pady=5)
        return

    if is_model_installed(model_name): #if the model is install then ask if the user wants to run it 
        result_label.configure(text=f"Model '{model_name}' is already installed.", text_color="green")

        wanna_run_entry = ctk.CTkEntry(app, placeholder_text="Do you want to run it? [Y/N]")
        wanna_run_entry.pack(pady=5)
        wanna_run_button = ctk.CTkButton(app, text="Submit", command=lambda: handle_run_decision(model_name))
        wanna_run_button.pack(pady=5)
    else:
        result_label.configure(text=f"Model '{model_name}' is not installed. Install it now? (Y/N)", text_color="red")
        install_model_entry = ctk.CTkEntry(app, placeholder_text="Type Y to install model")
        install_model_entry.pack(pady=5)
        install_model_button = ctk.CTkButton(app, text="Submit", command=lambda: handle_model_decision(install_model_entry.get(), model_name))
        install_model_button.pack(pady=5)

#Button 
check_button = ctk.CTkButton(app, text="Check Model", command=check_model)
check_button.pack(pady=10)

#launch the  GUI 
if __name__ == "__main__":
    app.mainloop()



