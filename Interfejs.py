import customtkinter as ctk
import tkinter as tk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

conversations = {}
current_chat = None


def new_chat():
    global current_chat

    chat_name = f"Rozmowa {len(conversations)+1}"
    conversations[chat_name] = ""

    sidebar.insert("end", chat_name)
    sidebar.select_set("end")

    current_chat = chat_name
    chat_box.delete("1.0", "end")


def load_chat(event):
    global current_chat

    selection = sidebar.curselection()
    if not selection:
        return

    chat_name = sidebar.get(selection)
    current_chat = chat_name

    chat_box.delete("1.0", "end")
    chat_box.insert("end", conversations[chat_name])


def send_message():
    global current_chat

    text = entry.get()

    if text.strip() == "" or current_chat is None:
        return

    message = f"Ty: {text}\nAI: (tu będzie odpowiedź AI)\n\n"

    chat_box.insert("end", message)
    chat_box.see("end")

    conversations[current_chat] += message

    entry.delete(0, "end")


app = ctk.CTk()
app.geometry("900x550")
app.title("AI Assistant")

# --- SIDEBAR ---
sidebar_frame = ctk.CTkFrame(app, width=200)
sidebar_frame.pack(side="left", fill="y", padx=5, pady=5)

new_chat_btn = ctk.CTkButton(sidebar_frame, text="➕ Nowa rozmowa", command=new_chat)
new_chat_btn.pack(pady=10, padx=10)

sidebar = tk.Listbox(sidebar_frame)
sidebar.pack(fill="both", expand=True, padx=10, pady=10)
sidebar.bind("<<ListboxSelect>>", load_chat)

# --- MAIN CHAT ---
main_frame = ctk.CTkFrame(app)
main_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

chat_box = ctk.CTkTextbox(main_frame)
chat_box.pack(fill="both", expand=True, padx=10, pady=10)

entry = ctk.CTkEntry(main_frame, placeholder_text="Napisz wiadomość...")
entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)

send_btn = ctk.CTkButton(main_frame, text="Wyślij", command=send_message)
send_btn.pack(side="right", padx=10, pady=10)

new_chat()

app.mainloop()